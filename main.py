from download import *
import csv
from queue import Queue
from threading import Thread

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('requests').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

class DownloadWorker(Thread):
   def __init__(self, queueTask, queueResult):
       Thread.__init__(self)
       self.queueTask = queueTask
       self.queueResult = queueResult

   def run(self):
       while True:
           # Get the work from the queue and expand the tuple
           id = self.queueTask.get()
           row = get_exh_data(id)
           self.queueResult.put(row)

           collectedCount = self.queueResult.qsize()
           if collectedCount % 50 == 0:
               logger.info("Collected %i items" % collectedCount)

           self.queueTask.task_done()

def main():
    result_filename = 'data.tsv'
    output = open(result_filename, 'a')
    writer = csv.writer(output, delimiter='\t')
    writer.writerow(['id', 'link name', 'address', 'phone', 'fax', 'website', 'email', 'categories'])

    # Create a queue to communicate with the worker threads
    queueTask = Queue()
    queueResult = Queue()

    # Create N worker threads
    for x in range(8):
        worker = DownloadWorker(queueTask, queueResult)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()

    # Put the ids into tasks queue
    exh_ids = get_exh_ids()

    task_put_counter = 0
    for exh_id in exh_ids:
        queueTask.put(exh_id)
        task_put_counter += 1

    logger.info("Put %i tasks into task queue" % task_put_counter)

    # Causes the main thread to wait for the queue to finish processing all the tasks
    queueTask.join()
    logger.info("Results queue approximate size: %i" % queueResult.qsize())

    # Write results from results queue to csv file
    row_written_counter = 0
    while not queueResult.empty():
        row = queueResult.get()
        writer.writerow(row)
        row_written_counter += 1

    logger.info("Finished, wrote %i rows to %s file" % (row_written_counter, result_filename))

if __name__ == '__main__':
    main()