import sys

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

def replace_identifiers(karyotype_lines, chr_details):
    updated_lines = []
    species_data = {}
    av_values = []
    av_chr_pairs = []

    for line in karyotype_lines:
        parts = line.split()
        identifier = parts[3]
        av_value = parts[2]  # Extracting the avXX value
        av_values.append(av_value)
        if identifier in chr_details:
            new_identifier, species = chr_details[identifier]
            parts[3] = new_identifier
            chr_number = new_identifier.split('_')[-1]
            if chr_number=="chr24":
                chr_number="chrx"
            elif chr_number=="chr25":
                chr_number="chry"
            parts[-1] = chr_number
            updated_line = ' '.join(parts)
            av_chr_pairs.append((av_value, chr_number))  # Store av-chr pair
            if species not in species_data:
                species_data[species] = []
            species_data[species].append((updated_line, int(parts[4])))
        else:
            updated_lines.append(line)
    return updated_lines, species_data, av_values,av_chr_pairs

def sort_species_data(species_data):
    sorted_data = []
    for species, data in species_data.items():
        data.sort(key=lambda x: x[1], reverse=species == 'bb')
        sorted_data.extend([line for line, _ in data])
    return sorted_data

def write_to_file(lines, file_path):
    with open(file_path, 'w') as file:
        for line in lines:
            file.write(line + '\n')

def main(karyotype_file, chr_details_file, output_file):
    # Read the tables
    karyotype_lines = read_table(karyotype_file)
    chr_details_lines = read_table(chr_details_file)

    # Parse the chr_details table
    chr_details = parse_chr_details(chr_details_lines)

    # Replace identifiers in karyotype and separate by species
    updated_karyotype, species_data, av_values,av_chr_pairs = replace_identifiers(karyotype_lines, chr_details)

    # Sort data for each species
    sorted_karyotype = sort_species_data(species_data)

    # Combine sorted data with unclassified lines
    final_output = sorted_karyotype + updated_karyotype

    # Write the result to the output file
    write_to_file(final_output, output_file)
    
	# Print the avXX values as a comma-separated list
    print("Please paste the following into chromsome order in your circos.conf")
    print(','.join(av_values))

    #Print the color configuration:
    # Print av-chr pairs
    print("Please paste the following into the root level of your circos.conf")
    print("<colors>")
    for av, chr_num in av_chr_pairs:
        print(f"{av} = {chr_num}")
    print("</colors>")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py karyotype.txt chr_details.txt output.txt")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])
