import sys
import getopt
import re

PATH_TO_LOG = 'report/1000.log'

#-------------------------------------------------#
def parse_line(line):
	res = re.search('.+ step (.+?): loss = (.+?) .+$', line)
	if res:
		return (res.group(1), res.group(2))
	else:
		return (None, None)

#-------------------------------------------------#
def parse_file(path_to_log):
	print 'step; loss'
	with open(path_to_log, "r") as log_file:
		for line in log_file:
			(step, loss) = parse_line(line)
			if step:
				print '{}; {}'.format(step, loss)


#MAIN---------------------------------------------#
def main(argv=None):
	try:
		(opts, args) = getopt.getopt(argv[1:], 'hl:', ['help', 'log='])
	except getopt.GetoptError:
		print argv[0] + ' --log={logfile}'
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print argv[0] + ' --log={logfile}'
			sys.exit(2)
		elif opt in ("-l", "--log"):
			PATH_TO_LOG = arg
		else:
			continue
		
	parse_file(PATH_TO_LOG)

if __name__ == '__main__':
	main(sys.argv[0:])
