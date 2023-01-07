import soundfile
import sounddevice
import numpy as np
import threading
import queue
import time

num_channels = 8

DATA_TYPE = "float32"

class AudioFile(object):
	def __init__(self, audio_data, sample_rate=44100.0):
		self.audio_data = np.array(audio_data)
		self.sample_rate = sample_rate
		self.T = len(audio_data)*1.0/sample_rate
		self.t = 0
		self.samples = len(self.audio_data)
		self.volume = [1.0]*num_channels
		self.active = True

	def get(self, dt):
		num_out_samples = int(dt*self.sample_rate)
		out_data = np.zeros((num_out_samples,1))
		start_sample = int(self.t*self.sample_rate)	
		out_index = 0
		cur_sample = start_sample
		while out_index < len(out_data):
			out_data[out_index] = self.audio_data[cur_sample]
			out_index += 1
			cur_sample = (cur_sample + 1) % self.samples
		self.t = cur_sample/self.sample_rate
		return out_data

class AudioStreamer(object):
	def __init__(self, files, sample_rate=44100):
		self.sample_rate = sample_rate
		devices = sounddevice.query_devices()
		device = None
		index = 0
		for d in devices:
			if "USB" in d["name"]:
				device = d
				break
			index += 1
		self.audio_data = []
		self.volume = [1.0]*num_channels
		for f in files:
			audio_data, _ = soundfile.read(f, dtype=DATA_TYPE)
			self.audio_data.append(AudioFile(audio_data[:,0]))
		print(audio_data)	
		self.out_stream = sounddevice.OutputStream(
			device=index,
			dtype=DATA_TYPE
			)
		self.out_stream.start()
		self.data_queue = queue.Queue()
		self.volume_mutex = threading.Lock()
		
	def set_channel_volume(self, channel, volume):
		self.volume_mutex.acquire()
		self.volume[channel] = volume	
		self.volume_mutex.release()

	def set_file_volume(self, file, channel, volume):
		self.volume_mutex.acquire()
		if channel is None:
			for i in range(len(self.audio_data[file].volume)):
				self.audio_data[file].volume[i] = volume	
		else:
			self.audio_data[file].volume[channel] = volume	
		self.volume_mutex.release()

	def set_file_volume_fraction(self, file, channel, volume_fraction):
		self.volume_mutex.acquire()
		if channel is None:
			for i in range(len(self.audio_data[file].volume)):
				self.audio_data[file].volume[i] *= volume_fraction 
		else:
			self.audio_data[file].volume[channel] = volume	
		self.volume_mutex.release()

	def get_data(self, dt):
		while 1:
			num_samples = int(dt*self.sample_rate)
			full_x = np.zeros((num_samples,num_channels))
			self.volume_mutex.acquire()
			for x in self.audio_data:
				if x.active:
					thing = x.get(dt)
					for i in range(num_channels):
						full_x[:,i] += thing[:,0]*self.volume[i]*x.volume[i]
			self.volume_mutex.release()
			full_x = np.ascontiguousarray(full_x)
			full_x = np.float32(full_x)
			self.current_data = full_x
			while self.data_queue.qsize() > 1:
				time.sleep(dt)
			self.data_queue.put(full_x)

	def write(self):	
		while 1:
			new_data = self.data_queue.get()
			sounddevice.RawOutputStream.write(self.out_stream, new_data)

	def start(self):
		dt = 0.2
		self.write_thread = threading.Thread(target=self.write)
		self.get_thread = threading.Thread(target=self.get_data, args=(dt,))
		self.write_thread.start()
		self.get_thread.start()
		'''
		for i in range(20):
			time.sleep(0.5)
			self.set_file_volume(0, 7, i*1.0/20)
			self.set_file_volume(0, 6, 1 - i*1.0/20)
		'''

	def wait(self):
		self.write_thread.join()
		self.get_thread.join()

	def fade_thread(self, track_num, fade_time):
		pause_time = 0.1	
		num_loops = int(fade_time/pause_time)
		for i in range(num_loops):
			time.sleep(pause_time)
			self.set_file_volume_fraction(track_num, None, 0.95)
		self.audio_data[track_num].active = False
		
	def fade_out_track(self, track_num, fade_time):
		fade_thread = threading.Thread(target=self.fade_thread, args=(track_num, fade_time))
		fade_thread.start()

# Sounds
#
# - Birds
# - Leaves rustling
# - Rain
# - Thunder
# - Crickets 
# - Running Water
# - Various bugs
# - Wind 

if __name__ == "__main__":
	s = AudioStreamer(["harp.wav", "budgie.wav"])
	while 1:
		s.start()
		s.fade_out_track(0, 10)
		s.wait()
