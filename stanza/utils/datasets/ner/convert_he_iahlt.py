import os

from stanza.utils.conll import CoNLL
import stanza.utils.default_paths as default_paths
from stanza.utils.datasets.ner.utils import write_dataset

def extract_sentences(doc):
    sentences = []
    for sentence in doc.sentences:
        current_entity = "O"
        words = []
        for word in sentence.words:
            text = word.text
            misc = word.misc
            if misc is None:
                words.append((text, current_entity))
                continue
            pieces = misc.split("|")
            for piece in pieces:
                if piece.startswith("Entity="):
                    entity = piece.split("=", maxsplit=1)[1]
                    if entity.startswith("(") and entity.endswith(")"):
                        assert current_entity == 'O'
                        entity = entity[1:-1]
                    elif entity.startswith("("):
                        assert current_entity == 'O'
                        entity = entity[1:]
                        current_entity = entity
                    elif entity.endswith(")"):
                        entity = entity[:-1]
                        assert current_entity == entity
                        current_entity = "O"
                    else:
                        assert current_entity == entity
                    words.append((text, entity))
                    break
            else: # closes for loop
                words.append((text, current_entity))
        sentences.append(words)

    return sentences

def convert_iahlt(udbase, output_dir, short_name):
    shards = ("train", "dev", "test")
    ud_dataset = os.path.join(udbase, "UD_Hebrew-IAHLTknesset")
    base_filename = "he_iahltknesset-ud-%s.conllu"
    datasets = []

    for shard in shards:
        filename = os.path.join(ud_dataset, base_filename % shard)
        doc = CoNLL.conll2doc(filename)
        sentences = extract_sentences(doc)
        print("Read %d sentences from %s" % (len(sentences), filename))
        datasets.append(sentences)

    write_dataset(datasets, output_dir, short_name)

def main():
    paths = default_paths.get_default_paths()

    udbase = paths["UDBASE_GIT"]
    output_directory = paths["NER_DATA_DIR"]
    convert_iahlt(udbase, output_directory, "he_iahlt")

if __name__ == '__main__':
    main()