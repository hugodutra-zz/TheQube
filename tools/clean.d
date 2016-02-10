/**
	TheQube source cleaner
	Version 0.6

	this command-line utility cleans TheQube source code from byte code and other intermediary files.
	It should be placed in TheQube/tools folder.

	Copyright 2016, Andre Polykanine A.K.A. Menelion Elensúlë
	https://github.com/Oire
*/

module theqube.tools.cleaner;

import std.file;
import std.getopt;
import std.parallelism: parallel;
import std.string: format;
import std.stdio: stdout;
import std.conv: to;
import std.experimental.logger: FileLogger;

void main(string[] args) {
	bool verbose;
	string logFile;

	auto cliOptions = getopt(args,
			std.getopt.config.caseSensitive,
			std.getopt.config.passThrough,
			"verbose|v", "If set, each file is listed in the log", &verbose,
			"log", "If set, the results will be logged to a given file", &logFile
	);
	if (cliOptions.helpWanted) {
		defaultGetoptPrinter(format("Usage: %s [options].\nAvailable options:", args[0]), cliOptions.options);
	} else {
		auto logging = (logFile !is null && logFile != "")? new FileLogger(logFile): new FileLogger(stdout);
		try {
			auto dirIter = dirEntries("..", "{*.pyc,*.pyo,*.obj}", SpanMode.depth);
			foreach(dirFile; parallel(dirIter, 1)) {
				try {
					remove(dirFile);
					if (verbose) {
						logging.infof("%s: removed", dirFile);
					}
				} catch(Exception e) {
					logging.errorf("Unable to remove %s: %s", dirFile, to!string(e));
				}
			}
		} catch(Exception e) {
			logging.errorf("Unable to traverse TheQube source folder: %s", to!string(e));
		}
	}
}