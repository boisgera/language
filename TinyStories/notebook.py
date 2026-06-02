import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import datasets as ds
    import pandas as pd
    import tqdm

    return ds, mo, tqdm


@app.cell
def _(ds):
    dataset = ds.load_dataset("karpathy/tinystories-gpt4-clean")
    return (dataset,)


@app.cell
def _(dataset):
    dataset["train"]
    return


@app.cell
def _():
    2_732_634 / 100 / 2 / 60 # hours
    return


@app.cell
def _(dataset):
    dataset["train"][0]
    return


@app.cell
def _(dataset):
    print(dataset["train"][0]["text"])
    return


@app.cell
def _(dataset, mo):
    mo.md(dataset["train"][0]["text"].replace("\n", "\n\n"))
    return


@app.cell
def _():
    def all_char_codes(dataset):
        codes = set()
        for text in dataset: 
            codes = codes.union({ord(c) for c in text})
        l = list(codes)
        l.sort()
        return l
    #print(all_char_codes(dataset["train"][:]["text"]))
    return


@app.cell
def _(dataset, tqdm):
    def train_tokenizer(dataset, extra_tokens):
        """
        Input: list of ASCII text and number of tokens to be stamped
        Output: merge rules
        """
        corpus = [list(text.encode("ascii")) for text in dataset]
        new_token = 256
        merge_rules = []
        for _ in tqdm.tqdm(range(extra_tokens)):
        
            # Find the most frequent digram
            digram_count = {}
            for tokens in corpus:
                for digram in zip(tokens[:-1], tokens[1:]):
                    digram_count[digram] = digram_count.get(digram, 0) + 1
            top_digram = max(digram_count, key=digram_count.get)
            # print(top_digram, digram_count[top_digram])
            merge_rules.append((new_token, top_digram))
        
            # Merge the digram
            for i, tokens in enumerate(corpus):
                new_tokens = []
                j = 0
                while j < len(tokens) - 1:
                    if (tokens[j], tokens[j + 1]) == top_digram:
                        new_tokens.append(new_token)
                        j += 2
                    else:
                        new_tokens.append(tokens[j])
                        j += 1
                if j == len(tokens) - 1:
                    new_tokens.append(tokens[j])
                corpus[i] = new_tokens
        
            new_token += 1
        return merge_rules

    merge_rules = train_tokenizer(dataset["train"][:100]["text"], extra_tokens=4_000)
    return (merge_rules,)


@app.cell
def _(merge_rules):
    print(merge_rules)
    return


@app.cell
def _(merge_rules):
    def display_tokens(merge_rules):
        token_to_text = {i: chr(i) for i in [10] + list(range(32, 127))}
        for merge_rule in merge_rules:
            new_token, (token_1, token_2) = merge_rule
            text = token_to_text[token_1] + token_to_text[token_2]
            token_to_text[new_token] = text
        return token_to_text

    print(display_tokens(merge_rules))
    return


if __name__ == "__main__":
    app.run()
