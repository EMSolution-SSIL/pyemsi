from pyemsi.FemapConverter import FemapConverter
import yappi
import pyemsi
import logging

file_handler = logging.FileHandler("pyemsi.log")
pyemsi.configure_logging(logging.DEBUG, handler=file_handler)

# Start yappi profiler (supports threading)
yappi.set_clock_type("cpu")
yappi.start()

# cv = FemapConverter(r"C:\Users\eskan\OneDrive\Desktop\delme\Trans_Voltage", output_name="transient", current=None)
cv = FemapConverter(r"C:\Users\eskan\OneDrive\Desktop\delme\Project\transient", force_2d=True)
cv.run()

# Stop profiler and save stats in cProfile format for compatibility with tuna
yappi.stop()
stats = yappi.get_func_stats()
stats.save("femap_profile.prof", type="pstat")
