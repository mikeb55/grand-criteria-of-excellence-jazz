import struct

class MIDIWriter:
    def __init__(self):
        self.tracks = []
        self.ticks_per_beat = 480

    def add_track(self, name):
        track = []
        self.tracks.append(track)
        return len(self.tracks) - 1

    def add_note(self, track_idx, channel, pitch, start_time, duration, velocity):
        on_time = int(start_time * self.ticks_per_beat)
        off_time = int((start_time + duration) * self.ticks_per_beat)
        # Note On
        self.tracks[track_idx].append((on_time, 0x90, channel, pitch, velocity))
        # Note Off
        self.tracks[track_idx].append((off_time, 0x80, channel, pitch, 0))

    def add_program_change(self, track_idx, channel, program):
        # Program Change is 0xC0. 2 bytes: Status+Channel, Program
        # We store as tuple. 
        # For compatibility with write loop which expects (time, type, ch, d1, d2),
        # we can use a special marker or just handle it.
        # Let's normalize storage to: (time, bytes_list)
        pass

    # Refactored storage to generic events
    def add_generic_event(self, track_idx, time, data_bytes):
        tick_time = int(time * self.ticks_per_beat)
        self.tracks[track_idx].append((tick_time, data_bytes))

    def write_var_len(self, value):
        if value == 0: return bytearray([0])
        bytes_list = []
        while value > 0:
            bytes_list.append(value & 0x7F)
            value >>= 7
        for i in range(1, len(bytes_list)):
            bytes_list[i] |= 0x80
        return bytearray(reversed(bytes_list))

    def write(self, filename):
        with open(filename, "wb") as f:
            f.write(b'MThd')
            f.write(struct.pack('>L', 6))
            f.write(struct.pack('>HHH', 1, len(self.tracks), self.ticks_per_beat))
            
            for track in self.tracks:
                # Sort by time
                track.sort(key=lambda x: x[0])
                
                data = bytearray()
                last_time = 0
                
                for event in track:
                    time, msg_bytes = event
                    delta = time - last_time
                    last_time = time
                    
                    data.extend(self.write_var_len(delta))
                    data.extend(msg_bytes)
                    
                # End of Track
                data.extend(self.write_var_len(0))
                data.extend(b'\xFF\x2F\x00')
                
                f.write(b'MTrk')
                f.write(struct.pack('>L', len(data)))
                f.write(data)

# Wrapper to maintain API compatibility with existing calls
class MIDIWriterWrapper(MIDIWriter):
    def add_note(self, track_idx, channel, pitch, start_time, duration, velocity):
        # Note On
        self.add_generic_event(track_idx, start_time, bytes([0x90 | (channel & 0x0F), pitch, velocity]))
        # Note Off
        self.add_generic_event(track_idx, start_time + duration, bytes([0x80 | (channel & 0x0F), pitch, 0]))

    def add_program_change(self, track_idx, channel, program):
        self.add_generic_event(track_idx, 0, bytes([0xC0 | (channel & 0x0F), program & 0x7F]))

