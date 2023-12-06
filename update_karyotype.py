import argparse

def read_table(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def parse_chr_details(lines):
    mapping = {}
    for line in lines:
        parts = line.split('\t')
        if len(parts) == 4:
            species_formatted = parts[1].replace(' ', '_')
            mapping[parts[2]] = (f"{species_formatted}_chr{parts[0]}", parts[1])
    return mapping

def process_karyotype(karyotype_lines, chr_details):
    updated_lines = []
    av_chr_pairs = []
    species_data = {}

    for line in karyotype_lines:
        parts = line.split()
        identifier, av_value = parts[3], parts[2]
        if identifier in chr_details:
            new_identifier, species = chr_details[identifier]
            chr_number = new_identifier.split('_')[-1]
            original_chr_number = chr_number.replace("chr","")
            chr_number = "chrx" if chr_number == "chr24" else "chry" if chr_number == "chr25" else chr_number
            parts[3], parts[-1] = new_identifier, chr_number
            updated_line = ' '.join(parts)
            size = int(parts[5])
            av_chr_pairs.append((av_value, chr_number, species, size,original_chr_number))
            species_data.setdefault(species, []).append((updated_line, size))
        else:
            updated_lines.append(line)

    return updated_lines, species_data, av_chr_pairs

def sort_data(species_data, av_chr_pairs,sort_by_chr_number):
    sorted_karyotype = []
    for species, data in species_data.items():
        data.sort(key=lambda x: x[1], reverse=species == 'bb')
        sorted_karyotype.extend([line for line, _ in data])
    
    # Corrected sorting logic for av_chr_pairs
    if sort_by_chr_number:
         av_chr_pairs.sort(key=lambda x: (x[2], int(x[4]) if x[2] =='bb' else -int(x[4])))
    else:
        av_chr_pairs.sort(key=lambda x: (x[2], -x[3] if x[2] == 'bb' else x[3]))
    return sorted_karyotype, av_chr_pairs


def write_to_file(lines, file_path):
    with open(file_path, 'w') as file:
        for line in lines:
            file.write(line + '\n')

def print_output(av_chr_pairs):
    print("Please paste the following into chromosome order in your circos.conf")
    sorted_av_values = [av for av, _, _, _ ,_ in av_chr_pairs]
    print(','.join(sorted_av_values))

    print("Please paste the following into the root level of your circos.conf")
    print("<colors>")
    for av_value, chr_number, _, _,_ in av_chr_pairs:
        print(f"{av_value} = {chr_number}")
    print("</colors>")

def main():
    parser = argparse.ArgumentParser(description='Process karyotype and chromosome details.')
    parser.add_argument('karyotype_file', type=str, help='Path to karyotype file')
    parser.add_argument('chr_details_file', type=str, help='Path to chromosome details file')
    parser.add_argument('output_file', type=str, help='Path to output file')
    parser.add_argument('--sort_by_chr_number', action='store_true', help='Sort by chromosome number')

    args = parser.parse_args()

    karyotype_lines = read_table(args.karyotype_file)
    chr_details_lines = read_table(args.chr_details_file)
    chr_details = parse_chr_details(chr_details_lines)

    updated_karyotype, species_data, av_chr_pairs = process_karyotype(karyotype_lines, chr_details)
    sorted_karyotype, sorted_av_chr_pairs = sort_data(species_data, av_chr_pairs, args.sort_by_chr_number)

    final_output = sorted_karyotype + updated_karyotype
    write_to_file(final_output, args.output_file)
    print_output(sorted_av_chr_pairs)

if __name__ == "__main__":
    main()

