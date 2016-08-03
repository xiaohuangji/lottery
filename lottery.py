import requests
import json
import time
import logging

URL='http://www.168kai.org/open/currentopen?code=10016'

logger = logging.getLogger("lottery")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

fh = logging.FileHandler("lottery.log")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)

class Lottery:

    _five_key_numbers=[]
    _consecutive_hit_number=0
    _first_and_second_rounds=[]
    _lastest_round=[]

    def _get_data(self):
        try:
            response = requests.get(URL)
            if response.ok:
                return response.text
        except:
            return None

    def _parse_data(self,text,n):
        if text is None: return []
        slots=[]
        j = json.loads(text)
        for e in j.get('list')[0:n]:
            slots.append(map(int,e.get('c_r').split(',')))
        return slots

    def get_lastest_data(self,n):
        slots=self._parse_data(self._get_data(),n)
        return slots


    def fill_first_and_second_rounds(self):
        self._first_and_second_rounds=self.get_lastest_data(2)
        logger.info('Fill first and second rounds numbers'+str(self._first_and_second_rounds))

    def update_laster_round(self,numbers):
        self._lastest_round=numbers

    def fill_five_key_numbers(self):
        CONSTANT=7
        k1=self._first_and_second_rounds[1][0]#first number of first-round
        k2=self._first_and_second_rounds[0][0]#first number of second-round
        k=k1+k2+CONSTANT if(k1+k2)<10 else k1+k2-10+CONSTANT

        i=k-3#start from k-2 k-1 k k+1 k+2
        l=len(self._first_and_second_rounds[1])
        for index in range(5):
            if i>=l:
                self._five_key_numbers.append(self._first_and_second_rounds[0][i % l])
            else:
                self._five_key_numbers.append(self._first_and_second_rounds[0][i])
            i+=1

        logger.info('Fill five key numbers'+str(self._five_key_numbers))


    def vacuum(self):
        self._first_and_second_rounds=[]
        self._five_key_numbers=[]
        self._consecutive_hit_number=0
        logger.warn('vacuum record...')

    def win(self):
        logger.warn('Win! Current five key numbers are:'+str(self._five_key_numbers))

    def calc(self,lastest_round):
        HIT=5
        if lastest_round[0] not in self._five_key_numbers:
            self._consecutive_hit_number+=1
            logger.info('Score! lastest round[0] not in five key numbers(hit++), '+str(self._consecutive_hit_number))
            if self._consecutive_hit_number==HIT:
                ##score!
                self.win()
                ##resume the whole process
                self.vacuum()
        else:
            self.vacuum()
            logger.warn('lastest round[0] appear, vacuum/resume(hit=0) '+str(self._consecutive_hit_number))

    def _compare_two_rounds(self,round1,round2):
        for i in range(0,len(round1)):
            if round1[i]==round2[i]:
                continue
            else:
                return False
        return True

    def run(self):
        INTERVAL=100#get data from website every Interval seconds
        while True:
            try:
                if not self._first_and_second_rounds:
                    self.fill_first_and_second_rounds()
                    self.fill_five_key_numbers()
                    self.update_laster_round(self.get_lastest_data(1)[0])
                lastest_round=self.get_lastest_data(1)[0]

                logger.debug('Lastest round is: '+str(lastest_round))
                if self._compare_two_rounds(lastest_round,self._lastest_round):
                    logger.debug('Waiting one lastest lottery...')
                else:
                    self.update_laster_round(lastest_round)
                    self.calc(lastest_round)
            except:
                self.vacuum()
                logger.warn('No enough data, waiting...')
            time.sleep(INTERVAL)

def main():
    lottery=Lottery()
    lottery.run()


if __name__ == '__main__':
    exit(main())
