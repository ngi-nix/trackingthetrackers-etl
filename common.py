#!/usr/bin/env python3



def load_psl(filename: str):
    with open(filename) as f:
        lines = [line.rstrip() for line in f]
        lines = [l for l in lines if l and '//' not in l]
        return lines

