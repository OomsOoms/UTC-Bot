from java.io import File
from java.net import URLClassLoader
from java.util import ArrayList

def generate_scram():
    # Load TNoodle classes
    tnoodle_jar = File("tnoodle.jar")
    class_loader = URLClassLoader.newInstance([tnoodle_jar.toURL()], getClass().getClassLoader())
    scramble_class = class_loader.loadClass("net.gnehzr.tnoodle.scrambles.ScramblePlugin")

    # Create a ScramblePlugin instance
    scramble_plugin = scramble_class.newInstance()

    # Generate a scramble
    scramble = scramble_plugin.generateScramble("333", 0)

    print(scramble)

generate_scram()
