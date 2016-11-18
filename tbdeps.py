#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Generate a Makefile for syzygy table generation"""

from __future__ import print_function

import argparse
import chess.syzygy


def default_args(args):
    if args.tbgenp is None:
        args.tbgenp = args.tbgen + "p"

    if args.wdl_suffix is None:
        if "atbgenp" in args.tbgenp:
            args.wdl_suffix = ".atbw"
        elif "stbgenp" in args.tbgenp:
            args.wdl_suffix = ".stbw"
        elif "gtbgenp" in args.tbgenp:
            args.wdl_suffix = ".gtbw"
        else:
            args.wdl_suffix = ".rtbw"

    if args.dtz_suffix is None:
        if "atbgenp" in args.tbgenp:
            args.dtz_suffix = ".atbz"
        elif "stbgenp" in args.tbgenp:
            args.dtz_suffix = ".stbz"
        elif "gtbgenp" in args.tbgenp:
            args.dtz_suffix = ".gtbz"
        else:
            args.dtz_suffix = ".rtbz"

    if args.pawnless_wdl_suffix is None:
        if "atbgen" in args.tbgen:
            args.pawnless_wdl_suffix = ".atbw"
        elif "stbgen" in args.tbgen:
            args.pawnless_wdl_suffix = ".stbw"
        elif "gtbgen" in args.tbgen:
            args.pawnless_wdl_suffix = ".gtbw"
        else:
            args.pawnless_wdl_suffix = ".rtbw"

    if args.pawnless_dtz_suffix is None:
        if "atbgen" in args.tbgen:
            args.pawnless_dtz_suffix = ".atbz"
        elif "stbgen" in args.tbgen:
            args.pawnless_dtz_suffix = ".stbz"
        elif "gtbgen" in args.tbgen:
            args.pawnless_dtz_suffix = ".gtbz"
        else:
            args.pawnless_dtz_suffix = ".rtbz"

    if args.pawnless_dtz_suffix is None:
        args.pawnless_dtz_suffix = args.dtz_suffix

    if args.one_king is None:
        args.one_king = not (("stbgenp" in args.tbgenp) or ("gtbgenp" in args.tbgenp))

    return args


def tbgen(command, args):
    builder = [command]
    if args.threads:
        builder.append("--threads")
        builder.append(str(args.threads))
    if args.wdl:
        builder.append("--wdl")
    if args.dtz:
        builder.append("--dtz")
    if args.stats:
        builder.append("--stats")
    if args.disk:
        builder.append("--disk")
    return " ".join(builder)


def dtzname(egname, args):
    if args.dtz or not args.wdl:
        suffix = args.dtz_suffix if "P" in egname else args.pawnless_dtz_suffix
    else:
        suffix = args.wdl_suffix if "P" in egname else args.pawnless_wdl_suffix

    return egname + suffix

def main(args):
    print("TBGEN =", tbgen(args.tbgen, args))
    print("TBGENP =", tbgen(args.tbgenp, args))

    closed = set()
    if args.one_king:
        closed.add("KvK")

    targets = list(args.endgames)

    if targets:
        print()
        print("all:", " ".join(dtzname(target, args) for target in targets))

    while targets:
        target = chess.syzygy.normalize_filename(targets.pop(0))
        if target in closed:
            continue

        closed.add(target)

        deps = list(chess.syzygy.dependencies(target, one_king=args.one_king))

        targets.extend(deps)

        print()
        print(("%s: %s" % (dtzname(target, args), " ".join(dtzname(dep, args) for dep in deps))).rstrip())
        print("\t%s %s" % ("$(TBGENP)" if "P" in target else "$(TBGEN)", target))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--threads", "-t", type=int, help="Use n threads. If no other tasks are running, it is recommended to set n to the number of CPU cores, or if the CPU supports hyperthreading, to the number of CPU hyperthreads.")
    parser.add_argument("--wdl", "-w", action="store_true", help="Only compress and save WDL files")
    parser.add_argument("--dtz", "-z", action="store_true", help="Only compress and save DTZ files")
    # parser.add_argument("-g", action="store_true", help="Generate the table but do not compress or save")
    parser.add_argument("--stats", "-s", action="store_true", help="Save statistics.")
    parser.add_argument("--disk", "-d", action="store_true", help="Reduce RAM usage during compression. This takes a bit more time because tables are temporarily saved to disk. This option is nescessary to generate 6-piece tables on systems with 16 GB RAM. This option is not needed on systems with 24 GB RAM or more.")

    parser.add_argument("--tbgen", default="rtbgen", help="The tablebase generator to use")
    parser.add_argument("--tbgenp")

    parser.add_argument("--wdl-suffix", default=None)
    parser.add_argument("--pawnless-wdl-suffix", default=None)
    parser.add_argument("--dtz-suffix", default=None)
    parser.add_argument("--pawnless-dtz-suffix", default=None)
    parser.add_argument("--one-king", action="store_true", default=None)
    parser.add_argument("--not-one-king", action="store_false", dest="one_king", default=None)

    parser.add_argument("endgames", nargs="*")

    main(default_args(parser.parse_args()))
