from pyemsi import FemapConverter, Plotter, configure_logging
import yappi
import logging
import pyvista as pv

file_handler = logging.FileHandler("pyemsi.log")
configure_logging(logging.DEBUG, handler=file_handler)

# Start yappi profiler (supports threading)
yappi.set_clock_type("cpu")
yappi.start()

# cv = FemapConverter(r"C:\Users\eskan\OneDrive\Desktop\delme\Trans_Voltage", output_name="transient", current=None)
# cv = FemapConverter(r"C:\Users\eskan\OneDrive\Desktop\delme\Project\transient", force_2d=True)
# cv.run()

file_path = r"C:\Users\eskan\OneDrive\Documents\Github\pyemsi\.pyemsi\output.pvd"

Plotter(file_path).set_scalar("Flux (A/m)", mode="node").show()


plt1 = Plotter(file_path)
plt1.reader.set_active_time_point(-1)
plt1.plotter.view_xy()
plt1.set_scalar("B-Mag (T)", mode="element", cell2point=True).show()


plt3 = Plotter()
plt3.plotter.add_mesh(pv.Sphere())
plt3.show()


# Stop profiler and save stats in cProfile format for compatibility with tuna
yappi.stop()
stats = yappi.get_func_stats()
stats.save("femap_profile.prof", type="pstat")
