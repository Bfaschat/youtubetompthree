from setuptools import setup, find_packages

setup(
    name='youtubetompthree',
    version='1.1.0',
    description='Telegram bot to download songs from Youtube',
    author='Jon Ander Besga',
    author_email='jon@wearejavit.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    entry_points={  # Optional
        'console_scripts': [
            'youtubetompthree=youtubetompthree.__main__:run_webhook',
            'youtubetompthree-polling=youtubetompthree.__main__:run_polling'
        ],
    },
)
