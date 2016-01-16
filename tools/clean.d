/**
	TheQube source cleaner
	Version 0.1

	this command-line utility cleans TheQube source code from byte code and other intermediary files.
	It optionally takes a path to TheQube source. If the path is missing, it assumes it is situated in TheQube/tools folder, so the source is located at ../src.
	It also can take an output file name to log its progress.

	Copyright 2016, Andre Polykanine A.K.A. Menelion Elensúlë
	https://github.com/Oire
*/

module theqube.tools.cleaner;

import std.stdio;
import std.file;
import std.getopt;
import parallelism: parallel;

class SourceCleaner {
	bool verbose;
	string outFile;

	this(bool verbose, string outFile) {
		this.verbose = verbose;
		this.outFile = outFile;
	}

	final void output(T...)(in string text, in T params) const {
		if (this.outFile is null || this.outFile == "") {
			writefln(text, params);
		} else { // Output to a file
			auto f = File(this.outFile, "w");
			scope(exit) f.close();
			try {
				f.writefln(text, params);
			} catch(Exception e) {
				writefln("Unable to write to %s: %s", this.outFile, e.msg);
			}
		}
	}

	final void clean(in string srcPath) const {
		try {
			auto dirIter = dirEntries(srcPath, "{*.pyc,*.pyo,*.obj}", SpanMode.depth);
			foreach(dirFile; parallel(dirIter, 1)) {
				try {
					remove(dirFile);
					if (this.verbose) {
						this.output("%s: removed", dirFile);
					}
				} catch(Exception e) {
					this.output("Unable to remove %s: %s", dirFile, e.msg);
				}
			}
		} catch(Exception e) {
			this.output("Unable to traverse %s: %s", srcPath, e.msg);
		}
	}
}

void main(string[] args) {
	bool verbose;
	string outFile;
	auto cliOptions = getopt(args,
			std.getopt.config.caseSensitive,
			std.getopt.config.passThrough,
			"verbose|v", "If set, each file is listed in the output", &verbose,
			"output|o", "If set, the results will be output to a given file", &outFile
	);
	if (cliOptions.helpWanted) {
		defaultGetoptPrinter(format("Usage: %s [options] [sourcePath]. If sourcePath is not given, the cleaner will assume it's placed in theQube\tools folder.\nAvailable options:", args[0]), cliOptions.options);
	} else {
		srcPath = args.length < 2? "../src": args[1];
		auto cleaner = new SourceCleaner(verbose, outFile);
		try {
			cleaner.clean(srcPath);
		} catch(Exception e) {
			cleaner.output("Unable to process %s: %s", srcPath, e.msg);
		}
	}
}