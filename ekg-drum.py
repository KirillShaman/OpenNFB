class NullBlock(Block):
    output = Output()

    def init(self):
        self.create_input('input')

    def process(self):
        beat.append(self.input.new)


import numpy as np

class HeartAnalyser(Block):
    def init(self):
        self.create_input('input', buffer=250)

    beat = Output('Beat Event')


    def process(self):       
        square = self.input.data ** 2

        threshold = np.percentile(square, 98)

        if np.max(self.input.new) > threshold:
            beat.append([1.0])
        else:
            beat.append([0.0])

        #TODO: implement holdoff time


class MIDIDrum(Block):
    def init(self, port):
        import rtmidi2.MidiOut as MidiOut
        self.midi = MidiOut(0)

        self.create_input('pitch', default=440)
        self.create_input('velocity', default=1.0)
        self.create_input('trigger')

    def process(self):
        if self.trigger.posedge:
            pitch = self.pitch.value
            vel = self.velocity.value
            self.midi.send_note(0, pitch, vel)



class EKGDrumFlow(Flow):
    
    def init(self, context):
        RawEKG = context.get_channel('Channel 1', color='red', label='Raw with 50/60 Hz Noise')

        RAWOSCI = Oscilloscope('Raw Signal', channels=[RawEKG])
        RAWOSC1.autoscale(True)

        gridFilter = BandPass(1, 25, input=RawEKG)
        EKG = gridFilter.output
        EKG.color = 'green'

        RAWOSC1.channel[1] = EKG

        fftFilt = Spectrograph('Spectrogram', mode='waterfall')
        fftFilt.freq_range = gridFilter.range
        fftFilt.label = 'Frequency Spectrum'

        heart = HeartAnalyzer(input=EKG)

        BPM = TextBox('BPM', label='Heartbeats per minute')
        BPM.input = heart.bpm

        drum = MIDIDrum(0)
        drum.trigger = heart.beat


        self.RAWOSC1 = RAWOSC1
        self.fftFilt = fftFilt


    def widget(self):
        w = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        w.setLayout(layout)

        layout.addWidget(self.RAWOSC1, 0, 0)
        layout.addWidget(self.fftFilt, 2, 0)

        return w


    def process(self):
        pass
