#
# Ableton Bridge hack
#

from __future__ import with_statement
import Live
import time
from _Framework.ControlSurface import ControlSurface
from _Framework.SessionComponent import SessionComponent

import array
import json

CHANNEL = 8
is_momentary = True

class AbletonBridge(ControlSurface):
  __module__ = __name__
  __doc__ = "Script that creates AbletonBridge"

  def __init__(self, c_instance):
    ControlSurface.__init__(self, c_instance)
    self.log_message("Hello from ")
    with self.component_guard():
      self._setup_session_control()
      self.set_highlighting_session_component(self.session)
    # song = self.song()
    # track = song.view.selected_track
    # self.log_message("Dir Track %r" % dir(track))
    # self.log_message("Track %r" % (track))
    # playing_slot_index = song.view.selected_track.playing_slot_index
    # self.log_message("Playing slot index %d" % (playing_slot_index))
    # if playing_slot_index > -1:
    #     song.view.selected_scene = song.scenes[playing_slot_index]
    #     if song.view.highlighted_clip_slot.has_clip:
    #         self.application().view.show_view('Detail/Clip')
    # self.log_message("Sending sysex")
    # midi_bytes = (0xF0, 0, 32, 41, 2, 10, 0xF7)
    # ControlSurface._send_midi(self, midi_bytes, optimized=False)
    # clip_slot = song.view.highlighted_clip_slot
    # self.log_message("Dir Clip slot %r" % dir(clip_slot))
    # self.log_message("Clip slot %r" % (clip_slot))
    # clip_slot.create_clip()
    # clip_slot.create_clip(4)
    # clip = clip_slot.clip
    # self.log_message("Clip %r" % (clip))
    # # cs.clip.remove_notes(0.0, 0, cs.clip.length, 127)
    # time = 0
    # pitch = 36
    # mute = False
    # velocity = 127
    # note1 = (36, 0, 1, 127, False)
    # note2 = (48, 1, 1, 127, False)
    # note3 = (36, 2, 1, 127, False)
    # note4 = (36, 3, 1, 127, False)
    # clip.set_notes((note1, note2, note3, note4, ))
    # clip.deselect_all_notes()
    # bgthread = BgThread(self.log_message)
    # bgthread.start()
    # sent_successfully =

  def _handle_time_request(self, request):
    response = { 'D': 'time' }
    return response

  def _handle_tracks_request(self, request):
    tr = []
    tracks = self.song().tracks
    self.log_message("tracks %r" % (tracks))
    for k in range(0, 7):
      trackout = {
        "i": k
      }
      if k < len(tracks):
        t = tracks[k]
        self.log_message("track %r" % (t))

        trackout["solo"] = t.solo
        trackout["mute"] = t.mute
        trackout["vol"] = t.mixer_device.volume.value
        trackout["s0"] = t.mixer_device.sends[0].value
        trackout["s1"] = t.mixer_device.sends[1].value

        clipsout = []
        for csi in range(0, len(t.clip_slots)):
            cs = t.clip_slots[csi]
            if cs.has_clip: # and cs.is_playing:
                clipsout.append({
                  "i": csi,
                  "playing": cs.is_playing,
                  "cued": cs.is_triggered,
                })

        trackout["clips"] = clipsout

      tr.append(trackout)
    response = { 'D': 'tracks', "tracks": tr }
    return response

  def _handle_clipnotes_request(self, request):
    response = { 'D': 'time' }
    tr = request['TR']
    sl = request['SL']
    tracks = self.song().tracks
    response = {
      "D": "clip-notes",
      "TR": tr,
      "SL": sl,
    }
    if tr < 0:
      return response
    if tr >= len(tracks):
      return response
    track = tracks[tr]
    if sl < 0:
      return response
    if sl >= len(track.clip_slots):
      return response
    slot = track.clip_slots[sl]
    if not slot.has_clip:
      return response
    clip = slot.clip
    notes = clip.get_notes(0.0, 0, clip.length, 127)
    outnotes = []
    for note in notes:
      if not note[4]:
        outnotes.append({
          "N": note[0],
          "S": note[1],
          "L": note[2],
          "V": note[3],
        })
    # notes = clip.get_notes()
    response["notes"] = outnotes
    return response

  def _handle_trackprops_request(self, request):
    pass

  def _handle_setnotes_request(self, request):
    response = { 'D': 'time' }
    tr = request['TR']
    sl = request['SL']
    tracks = self.song().tracks
    response = {
      "D": "clip-notes",
      "TR": tr,
      "SL": sl,
    }
    if tr < 0:
      return response
    if tr >= len(tracks):
      return response
    track = tracks[tr]
    if sl < 0:
      return response
    slot = track.clip_slots[sl]
    if not slot.has_clip:
      slot.create_clip(4)
    clip = slot.clip
    clipnotes = []
    for innote in request["notes"]:
      clipnotes.append(tuple([
        innote['N'],
        innote['S'],
        innote['D'],
        innote['V'],
        False
      ]))
    clip.remove_notes(0.0, 0, clip.length * 32, 127)
    clip.set_notes(tuple(clipnotes))
    clip.deselect_all_notes()

  def _handle_json_request(self, request):
    self.log_message("Json request %r" % (request))
    resp = None
    if 'Q' in request:
      if request['Q'] == 'time':
        resp = self._handle_time_request(request)
      if request['Q'] == 'tracks':
        resp = self._handle_tracks_request(request)
      if request['Q'] == 'clip-notes':
        resp = self._handle_clipnotes_request(request)
    if 'A' in request:
      if request['A'] == 'track-props':
        resp = self._handle_trackprops_request(request)
      if request['A'] == 'set-notes':
        resp = self._handle_setnotes_request(request)
    if resp:
      self._send_json_response(resp)


  def _send_json_response(self, response):
    self.log_message("Send json response %r" % (response))
    bytes = array.array('B', json.dumps(response)).tolist()
    self.log_message("Send bytes %r" % (bytes))
    bytes = [0xF0, 0x4A] + bytes + [0xF7]
    self.log_message("Send bytes %r" % (bytes))
    # midi_bytes2 = (240, 0, 32, 41, 2, 10, 119)
    ControlSurface._send_midi(self, tuple(bytes), optimized=False)

  def _setup_session_control(self):
    num_tracks = 8 #8 columns (tracks)
    num_scenes = 8 #8 rows (scenes)
    #(num_tracks, num_scenes) a session highlight ("red box")
    self.session = SessionComponent(num_tracks,num_scenes)
    self.session.set_offsets(0,0)

  def disconnect(self):
    ControlSurface.disconnect(self)
    return None

  def handle_sysex(self, midi_bytes):
    self.log_message("Got sysex", midi_bytes)
    if midi_bytes[0] == 0xF0 and midi_bytes[1] == 0x6A:
      # got request
      midi_bytes = midi_bytes[2:len(midi_bytes)-1]
      # self.log_message("Got json request", midi_bytes)
      jsonstr = array.array('B', midi_bytes).tostring()
      self.log_message("Got json request", jsonstr)
      self._handle_json_request(json.loads(jsonstr))
