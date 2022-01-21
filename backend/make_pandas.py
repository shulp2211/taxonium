import taxonium_pb2
import gzip
import tqdm
import pandas as pd

protobuf_location = "./nodelist.pb.gz"
print("Reading proto")

# Read in the protobuf file
with gzip.open(protobuf_location, "rb") as f:
    nodelist = taxonium_pb2.AllData()
    nodelist.ParseFromString(f.read())

print("Done reading proto")
# Create a new SQLite database with columns:
# id, x, y, name, parent_id, num_tips
# there should also be one column per item in nodelist.node_data.metadata_singles

for_df = {
    "node_id": range(len(nodelist.node_data.x)),
    "x": list(nodelist.node_data.x),
    "y": list(nodelist.node_data.y),
    "parent_id": list(nodelist.node_data.parents),
    "num_tips": list(nodelist.node_data.num_tips),
    "name": list(nodelist.node_data.names),
}

for metadata_single in nodelist.node_data.metadata_singles:
    for_df[f"meta_{metadata_single.metadata_name}"] = [
        metadata_single.mapping[x] for x in metadata_single.node_values
    ]

print("Creating dataframe")
df = pd.DataFrame(for_df)
# set the meta columns to categorical
for name in df.columns:
    if name.startswith("meta_"):
        df[name] = df[name].astype("category")
print("Done creating dataframe")

print(df)

# Write out in feather format
df.to_feather("../database/database.feather")

mutation_ids = []
previous_residues = []
residue_poses = []
new_residues = []
genes = []

for mutation_id, name in enumerate(nodelist.mutation_mapping):
    if name == "":
        continue
    gene, rest = name.split(":")
    previous_residue, residue_pos, new_residue = rest.split("_")
    previous_residues.append(previous_residue)
    residue_poses.append(residue_pos)
    new_residues.append(new_residue)
    mutation_ids.append(mutation_id)
    genes.append(gene)

mutation_table = pd.DataFrame({
    "mutation_id": mutation_ids,
    "previous_residue": previous_residues,
    "residue_pos": residue_poses,
    "new_residue": new_residues,
    "gene": genes
})

# set gene and residues to categorical
mutation_table["gene"] = mutation_table["gene"].astype("category")
mutation_table["previous_residue"] = mutation_table["previous_residue"].astype(
    "category")
mutation_table["new_residue"] = mutation_table["new_residue"].astype(
    "category")

mutation_table.to_feather("../database/mutation_table.feather")

node_ids = []
mutation_ids = []
for node_id, these_mutation_ids in enumerate(nodelist.node_data.mutations):
    for mutation_id in these_mutation_ids.mutation:
        node_ids.append(node_id)
        mutation_ids.append(mutation_id)

df = pd.DataFrame({"node_id": node_ids, "mutation_id": mutation_ids})

df.to_feather("../database/node_mutation_table.feather")