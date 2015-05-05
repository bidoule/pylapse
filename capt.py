import os
import shutil
import sys
import subprocess
import time
import datetime
import logging

import picamera

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

def capture(camera, directory, seconds):
    today = datetime.date.today()
    logging.info('Capturing {:%c}'.format(today))
    dirname = today.strftime('%Y-%m-%d')
    dirpath = os.path.join(directory, dirname)
    try:
        os.makedirs(dirpath)
    except OSError:
        pass
    filepath = os.path.join(dirpath, 'img{counter:05d}.jpg')
    try:
        for filename in camera.capture_continuous(filepath):
            logging.debug('\tCaptured %s'.format(filename))
            time.sleep(seconds)
            if datetime.date.today() > today:
                logging.info('End of the day')
                break
    except KeyboardInterrupt:
        logging.info("Exiting... but cleaning first")
        raise
    finally:
        logging.info('Making movie')
        make_movie(directory, today)


def make_movie(directory, date):
    dirname = date.strftime('%Y-%m-%d')
    dirpath = os.path.join(directory, dirname)
    filepath = os.path.join(dirpath, 'img%05d.jpg')
    moviepath = os.path.join(directory, dirname + '.mp4')
    subprocess.call(['avconv', '-f', 'image2', '-i', filepath, moviepath])
    shutil.rmtree(dirpath)


def parse_resolution(resolution):
    try:
        return tuple(int(r.strip()) for r in resolution.split('x'))
    except ValueError:
        raise ValueError("Wrong resolution format. Must be AAAxBBB")


def main(directory, seconds, resolution):
    try:
        os.makedirs(directory)
    except OSError:
        pass
    with picamera.PiCamera() as camera:
        camera.resolution = parse_resolution(resolution)
        while True:
            try:
                capture(camera, directory, seconds)
            except KeyboardInterrupt:
                logger.info('Exiting.')
                break
     

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Capture a timestampted picture")
    parser.add_argument('--directory', '-d', help="Directory to store files", default='data')
    parser.add_argument('--seconds', '-s', help="Seconds between two shots", default=15, type=int)
    parser.add_argument('--resolution', '-r', help="Resolution of camera", default='640x480')
    args = parser.parse_args()

    main(**vars(args))
