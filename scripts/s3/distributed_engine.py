import openai

from datasets import load_dataset
import sglang as sgl
from sglang import function, system, user, assistant, gen
from sglang.srt.managers.s3_utils import save_results
from tqdm import tqdm


@function
def summarize(s, article):
    s += system("Your task is to summarize the user given article in only one \
                 paragraph.")
    s += user(article)
    s += assistant(gen("summarization", max_tokens=256))


def main():
    dataset = load_dataset("/models/cnn_dailymail", split="test")
    runtime = sgl.Runtime(model_path="/models/Mixtral-8x7B-Instruct-v0.1",
                          disable_overlap_schedule=True,
                          dist_init_addr="192.168.100.12:50000",
                          tp_size=4,
                          nnodes=4,
                          node_rank=0,
                          disable_cuda_graph=True)
    sgl.set_default_backend(runtime)

    for id, article in tqdm(enumerate(dataset["article"])):
        # print(f"Summarizing Article {id}")
        state = summarize.run(article)
        input_text = None
        output_text = None
        for m in state.messages():
            # print(m["role"], ":", m["content"])
            if m["role"] == "user":
                input_text = m["content"]
            elif m["role"] == "assistant":
                output_text = m["content"]
        assert input_text is not None and output_text is not None
        save_results({
            "Input_text": input_text,
            "Output_text": output_text}, "test")

    # print(state["result"])

if __name__ == "__main__":
    main()