#include "llama.h"

#include <cstdlib>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

struct Arguments {
    std::string model_path;
    std::string prompt_path;
    int n_predict = 512;
    int threads = 1;
    uint32_t seed = 42;
    float temperature = 0.0F;
};

[[noreturn]] void usage(const char * program) {
    std::cerr << "usage: " << program
              << " --model MODEL --prompt PROMPT --n-predict 512 --threads N --seed 42 --temp 0\n";
    std::exit(EXIT_FAILURE);
}

Arguments parse_arguments(int argc, char ** argv) {
    Arguments args;

    for (int i = 1; i < argc; ++i) {
        const std::string option = argv[i];
        if (option == "--model" || option == "--prompt" || option == "--n-predict" ||
            option == "--threads" || option == "--seed" || option == "--temp") {
            if (++i == argc) {
                usage(argv[0]);
            }
            const std::string value = argv[i];
            if (option == "--model") {
                args.model_path = value;
            } else if (option == "--prompt") {
                args.prompt_path = value;
            } else if (option == "--n-predict") {
                args.n_predict = std::stoi(value);
            } else if (option == "--threads") {
                args.threads = std::stoi(value);
            } else if (option == "--temp") {
                args.temperature = std::stof(value);
            } else {
                args.seed = static_cast<uint32_t>(std::stoul(value));
            }
        } else {
            usage(argv[0]);
        }
    }

    if (args.model_path.empty() || args.prompt_path.empty() || args.n_predict <= 0 ||
        args.threads <= 0 || args.temperature != 0.0F) {
        usage(argv[0]);
    }
    return args;
}

std::string read_file(const std::string & path) {
    std::ifstream stream(path, std::ios::binary);
    if (!stream) {
        throw std::runtime_error("cannot read " + path);
    }
    return {std::istreambuf_iterator<char>(stream), std::istreambuf_iterator<char>()};
}

} // namespace

int main(int argc, char ** argv) {
    try {
        const Arguments args = parse_arguments(argc, argv);
        const std::string prompt = read_file(args.prompt_path);

        llama_backend_init();

        llama_model_params model_params = llama_model_default_params();
        model_params.n_gpu_layers = 0;
        llama_model * model = llama_model_load_from_file(args.model_path.c_str(), model_params);
        if (model == nullptr) {
            throw std::runtime_error("cannot load model");
        }

        llama_context_params context_params = llama_context_default_params();
        context_params.n_ctx = 4096;
        context_params.n_batch = 4096;
        context_params.n_threads = args.threads;
        context_params.n_threads_batch = args.threads;
        llama_context * context = llama_init_from_model(model, context_params);
        if (context == nullptr) {
            llama_model_free(model);
            throw std::runtime_error("cannot create inference context");
        }

        const llama_vocab * vocab = llama_model_get_vocab(model);
        std::vector<llama_token> prompt_tokens(prompt.size() + 16);
        int token_count = llama_tokenize(
            vocab,
            prompt.data(),
            static_cast<int32_t>(prompt.size()),
            prompt_tokens.data(),
            static_cast<int32_t>(prompt_tokens.size()),
            true,
            true);
        if (token_count < 0) {
            prompt_tokens.resize(static_cast<size_t>(-token_count));
            token_count = llama_tokenize(
                vocab,
                prompt.data(),
                static_cast<int32_t>(prompt.size()),
                prompt_tokens.data(),
                static_cast<int32_t>(prompt_tokens.size()),
                true,
                true);
        }
        if (token_count <= 0) {
            throw std::runtime_error("cannot tokenize prompt");
        }
        prompt_tokens.resize(static_cast<size_t>(token_count));

        llama_sampler_chain_params sampler_params = llama_sampler_chain_default_params();
        llama_sampler * sampler = llama_sampler_chain_init(sampler_params);
        llama_sampler_chain_add(sampler, llama_sampler_init_dist(args.seed));
        llama_sampler_chain_add(sampler, llama_sampler_init_greedy());

        llama_batch batch = llama_batch_get_one(
            prompt_tokens.data(),
            static_cast<int32_t>(prompt_tokens.size()));
        if (llama_decode(context, batch) != 0) {
            throw std::runtime_error("cannot decode prompt");
        }

        for (int i = 0; i < args.n_predict; ++i) {
            llama_token token = llama_sampler_sample(sampler, context, -1);
            if (llama_vocab_is_eog(vocab, token)) {
                break;
            }

            std::cout << token << '\n';
            llama_sampler_accept(sampler, token);
            batch = llama_batch_get_one(&token, 1);
            if (llama_decode(context, batch) != 0) {
                throw std::runtime_error("cannot decode generated token");
            }
        }

        llama_sampler_free(sampler);
        llama_free(context);
        llama_model_free(model);
        llama_backend_free();
        return EXIT_SUCCESS;
    } catch (const std::exception & error) {
        std::cerr << "token-id-runner: " << error.what() << '\n';
        return EXIT_FAILURE;
    }
}
