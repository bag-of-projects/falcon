import dis
import logging
import sys
import random
import time
import unittest 



logging.basicConfig(
    format='%(asctime)s %(filename)s:%(funcName)s %(message)s',
    level=logging.INFO, 
    stream=sys.stderr)

class TimedTest(unittest.TestCase):
  def timed(self, function, *args, **kw):
    return self.time_compare(function, *args, **kw)

  def time_compare(self, function, *args, **kw):
    try: import falcon
    except: falcon = None
    
    print 'Original bytecode, %s:\n' % function.func_name
    dis.dis(function)
    
    repeat = kw.get('repeat', 1)
    if falcon:
      evaluator = falcon.Evaluator()
      frame = evaluator.frame_from_python(function, args)
    
    for i in range(repeat):
      random.seed(10)
      st = time.time()
      py_result = function(*args)
      py_time = time.time() - st
     
      if falcon:
        random.seed(10)
        st = time.time()
        falcon_result = evaluator.eval(frame)
        f_time = time.time() - st
      else:
        f_time = 0
      
      logging.info('%s : Python: %.3f, Falcon: %.3f' % (function.func_name, py_time, f_time))
      if falcon:
          if isinstance(py_result, list):
              # long lists seem to take a bizarrely long time for assertEqual
              # so I added a special case here 
              assert isinstance(falcon_result, list), \
                "Expected list but got %s" % type(falcon_result)
              assert len(py_result) == len(falcon_result), \
                "Expected list of length %d but got list of %d" % \
                (len(py_result), len(falcon_result))
              for py_elt, falcon_elt in zip(py_result, falcon_result):
                assert py_elt == falcon_elt, "%s != %s" % (py_elt, falcon_elt)
          else:
              self.assertEqual(py_result, falcon_result)
