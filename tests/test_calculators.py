import unittest
from core.calculators import calculate_cidr, calculate_vlsm


class TestIPCalculators(unittest.TestCase):
    def test_cidr_standard(self):
        res = calculate_cidr("192.168.10.0/24")
        self.assertEqual(res["network"], "192.168.10.0")
        self.assertEqual(res["first_host"], "192.168.10.1")
        self.assertEqual(res["last_host"], "192.168.10.254")
        self.assertEqual(res["broadcast"], "192.168.10.255")
        self.assertEqual(res["usable_hosts"], 254)

    def test_vlsm_standard(self):
        reqs = [("A", 100), ("B", 50), ("C", 25), ("D", 10)]
        res = calculate_vlsm("192.168.0.0/24", reqs)
        allocs = res["allocations"]
        self.assertEqual(len(allocs), 4)
        self.assertEqual((allocs[0].network, allocs[0].prefix), ("192.168.0.0", 25))
        self.assertEqual((allocs[1].network, allocs[1].prefix), ("192.168.0.128", 26))
        self.assertEqual((allocs[2].network, allocs[2].prefix), ("192.168.0.192", 27))
        self.assertEqual((allocs[3].network, allocs[3].prefix), ("192.168.0.224", 28))
        self.assertEqual(res["remaining_addresses"], 16)

    def test_vlsm_overflow_error(self):
        with self.assertRaises(ValueError):
            calculate_vlsm("192.168.0.0/24", [("A", 200), ("B", 100)])


if __name__ == "__main__":
    unittest.main()