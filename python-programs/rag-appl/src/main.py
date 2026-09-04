from rag import PDFRAG


def display_sources(
    sources
):

    if not sources:
        return

    print()
    print("Sources")
    print("-" * 60)

    for source in sources:

        print(
            f"PDF: {source['source']}"
        )

        print(
            f"Page: {source['page']}"
        )

        print()


def main():

    print()
    print("=" * 60)
    print("LOCAL FAISS RAG APPLICATION")
    print("=" * 60)

    try:

        rag = PDFRAG()

    except Exception as error:

        print()
        print(
            f"Startup error: {error}"
        )

        return

    print()
    print("RAG application is ready.")
    print()
    print(
        "Type your question."
    )

    print(
        "Type 'exit' to quit."
    )

    print("=" * 60)

    while True:

        question = input(
            "\nQuestion: "
        ).strip()

        if not question:
            continue

        if question.lower() in {
            "exit",
            "quit"
        }:

            print(
                "\nApplication stopped."
            )

            break

        try:

            result = rag.ask(
                question
            )

            print()
            print("Answer")
            print("-" * 60)

            print(
                result["answer"]
            )

            display_sources(
                result["sources"]
            )

        except Exception as error:

            print()
            print(
                f"Error: {error}"
            )


if __name__ == "__main__":
    main()