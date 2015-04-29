import ast, time, itertools
import simplejson as json

## read msd subset as msd_list
def readMST(file):
  start = time.time()
  with open(file, 'r') as f:
    msd_raw = f.read().split('\n')[:-1]
    msd_list = map(lambda x: eval(x), msd_raw)
  end = time.time() - start
  # print "Time Cost: "+str(end)
  print "#lines processed: "+str(len(msd_list))
  return msd_list

lists = map(readMST, ['./search/data/msd2'])
msd_list = list(itertools.chain.from_iterable(lists))
# print msd_list[0].keys()
# print len(msd_list)

from search.models import MusicTrack

def saveData(track):
  print '\n'
  print track['title']
  print track['year']
  print track['tempo']
  print track['artist_name']
  print track['track_id']
  print track['duration']
  q = MusicTrack(name = track['title'], release = int(track['year']), tempo = float(track['tempo']), artist_name = (track['artist_name']), track_id = track['track_id'], duration = float(track['duration']))
  q.save()

print "Saving Data"
# print msd_list[0]
map(saveData, msd_list)