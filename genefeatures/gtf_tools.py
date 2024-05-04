from collections import OrderedDict

class GtfGff:


    def __init__(self):
        self._record_hashes = []
        self.records = OrderedDict()
        self.feature_index = {}
        self.seqname_index = {}
        self.attribute_index = {}
        self.metadata = {}
    
    def add_record(self, record: dict, linetype: str = "record", record_hash: int = None):

        if linetype == "meta":
            self.metadata.update(record)
            return

        if type(record) != dict:
            raise TypeError
        if  record_hash == None:
            record_hash = hash(str(record))
        
        self._record_hashes.append(record_hash)
        self.records[record_hash] = record
            
        feature_type = record["feature"]
        if feature_type not in self.feature_index.keys():
            self.feature_index[feature_type] = []
        self.feature_index[feature_type].append(record_hash)

        seqname = record["seqname"]
        if seqname not in self.seqname_index.keys():
            self.seqname_index[seqname] = []
        self.seqname_index[seqname].append(record_hash)

        # Indexing by attributes
        for attribute, value in record['attributes'].items():
            if attribute not in self.attribute_index:
                self.attribute_index[attribute] = {}
            if value not in self.attribute_index[attribute]:
                self.attribute_index[attribute][value] = []
            self.attribute_index[attribute][value].append(record_hash)
    
    def get_records_by_feature(self, feature_type):
        hashes = self.feature_index.get(feature_type, [])
        return [self.records[h] for h in hashes]
    
    def get_records_by_seqname(self, seqname):
        if isinstance(seqname, int):
            seqname = str(seqname)
        hashes = self.seqname_index.get(seqname, [])
        return [self.records[h] for h in hashes]
    
    def get_records_by_attribute(self, attribute, value):
        hashes = self.attribute_index.get(attribute, {}).get(value, [])
        return [self.records[h] for h in hashes]

    def __getitem__(self, idx):

        if type(idx) not in (int, slice, list):
            raise TypeError(f"Expected types int, slice, or list; got '{idx}' of type: {type(idx)}") 

        if isinstance(idx, int):
            return self.records[self._record_hashes[idx]]

        if isinstance(idx, slice):
            records = [
                self.records[self._record_hashes[i]] for i in range(
                    idx.start,
                    idx.stop,
                )
            ] 
            return records
        
        if isinstance(idx, list):
            return [self.records[self._record_hashes[i]] for i in idx]
    
    def __len__(self):
        return len(self._record_hashes)


    
def parse_gtf(filename, gtf = None):

    """
    Read GTF (Gene Transfer Format) or GFF (General Feature Format) files and parse the content.

    Parameters:
        file_path (str): The path to the GTF/GFF file.

    Returns:
        GtfGff data structure defined above
        
    """
    # if gtf is not give make one, if wrong type throw error
    if gtf == None:
        gtf = GtfGff()
    else:
        assert type(gtf) == GtfGff, f"gtf provided is not {GtfGff}, {type(gtf)} found\n"
    
    with open(filename, 'r') as file:
        for line in file:

            # Save comment lines as attributes
            if line.startswith('#'):
                record = line.lstrip("#!").rstrip("\n").split(" ")
                record = {record[0]: record[1]}
                gtf.add_record(record, linetype = "meta")
                continue

            # Split line by tab
            fields = line.strip().split('\t')
            # Parse attributes
            attributes = {}
            for attribute in fields[8].split(';'):
                key_value = attribute.strip().split(' ')
                if len(key_value) == 2:
                    attributes[key_value[0]] = key_value[1].strip('"')

            # Create feature dictionary
            record = {
                'seqname': fields[0],
                'source': fields[1],
                'feature': fields[2],
                'start': int(fields[3]),
                'end': int(fields[4]),
                'score': fields[5],
                'strand': fields[6],
                'frame': fields[7],
                'attributes': attributes
            }
            gtf.add_record(record, linetype = "record")
    
    return gtf

