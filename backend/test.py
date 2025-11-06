from pdf2image import convert_from_path

def main():
    # 1. Pass the file path (string) directly to convert_from_path
    pdf_path = './books/High Performance Python.pdf'
    output_filename = './test.jpg'

    # convert_from_path returns a list of Pillow Image objects
    # We set first_page=1 and last_page=1 to get only the front page.
    images = convert_from_path(
        pdf_path,
        first_page=1,
        last_page=1,
        fmt='jpg' # Specify the format for the resulting image object
    )

    # 2. Extract the first (and only) image from the list and explicitly save it.
    if images:
        front_page = images[0]
        front_page.save(output_filename)
        print(f"Front page saved to {output_filename}")
    else:
        print("Could not convert the front page.")

if __name__ == '__main__':
    main()