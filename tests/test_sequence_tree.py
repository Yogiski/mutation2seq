import unittest
from Bio.Seq import Seq
from genefeatures.sequence_tree import SequenceTree
from genefeatures import gtf_tools as gt


class TestSequenceTree(unittest.TestCase):

    def setUp(self):
        gtf = gt.parse_gtf("tests/data/test_hs_grch38.gtf")
        self.gtf = gtf.query(
            {
                "attributes": {"transcript_id": "ENST00000511072"}
            }
        )
        self.fasta = "tests/data/trunc_hs.grch38.dna.chr1.fa"

    def test_from_gtf(self):
        recs = self.gtf.export_records()
        print(recs[0])
        st = SequenceTree.from_gtf_gff(recs)
        self.assertIsInstance(st, SequenceTree)

        print(self.gtf[0])
        st = SequenceTree.from_gtf_gff(self.gtf)
        self.assertIsInstance(st, SequenceTree)

    def test_from_gtf_missing_start(self):
        with self.assertRaises(KeyError):
            recs = self.gtf.export_records()
            recs[0].pop("start")
            SequenceTree.from_gtf_gff(recs)

    def test_from_gtf_missing_seqname(self):
        with self.assertRaises(KeyError):
            recs = self.gtf.export_records()
            recs[0].pop("seqname")
            SequenceTree.from_gtf_gff(recs)

    def test_from_gtf_missing(self):
        with self.assertRaises(KeyError):
            recs = self.gtf.export_records()
            recs[0].pop("strand")
            SequenceTree.from_gtf_gff(recs)

    def test_from_gtf_multiple_seqnames(self):
        with self.assertRaises(ValueError):
            recs = self.gtf.export_records()
            recs[0]["seqname"] = "6"
            SequenceTree.from_gtf_gff(recs)

    def test_make_seq_index(self):
        st = SequenceTree()
        seq_idx = st._make_seq_index(500, 510)
        self.assertEqual(list(range(0, 11)), list(seq_idx.values()))

    def test_get_sequence(self):
        st = SequenceTree.from_gtf_gff(self.gtf)
        st.read_sequence(self.fasta)
        seq = st.sequence
        self.assertIsInstance(seq, Seq)
        self.assertIn("A" or "C" or "G" or "T", seq)

    def test_get_coding_seq(self):
        st = SequenceTree.from_gtf_gff(self.gtf)
        st.read_sequence(self.fasta)
        coding = st.get_coding_sequence()
        self.assertTrue(coding.startswith("ATG"))
        self.assertEqual(len(coding) % 3, 0)

    def test_translate(self):
        st = SequenceTree.from_gtf_gff(self.gtf)
        st.read_sequence(self.fasta)
        aa = st.translate()
        self.assertTrue(aa.startswith("M"))
        self.assertNotIn("*", aa)
