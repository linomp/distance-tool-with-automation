import asyncio
import os
import sys
from contextlib import contextmanager, redirect_stdout
from io import StringIO

import streamlit as st

from app import start_processing_loop

DATA_DIR = 'data'


@contextmanager
def st_capture(output_func):
    # Source: https://discuss.streamlit.io/t/cannot-print-the-terminal-output-in-streamlit/6602/2
    with StringIO() as stdout, redirect_stdout(stdout):
        old_write = stdout.write

        def new_write(string):
            ret = old_write(string)
            output_func(stdout.getvalue())
            return ret

        stdout.write = new_write
        yield


async def main():
    input_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.txt')]

    st.title('Distance Tool')
    st.write('Compute driving distances directly from Google Maps Website')

    def ff(delim):
        if delim == '\t':
            return 'tab'
        elif delim == ',':
            return 'comma'
        elif delim == ';':
            return 'semicolon'
        return delim

    with st.sidebar:
        input_filename = st.selectbox('Select input file', input_files)
        input_delimiter = st.selectbox('Input delimiter', options=['\t', ',', ';'], format_func=ff, index=0)
        output_filename = st.text_input('Output filename', value='output.csv')
        output_delimiter = st.selectbox('Output delimiter', options=['\t', ',', ';'], format_func=ff, index=0)

        with st.expander('Advanced options'):
            seconds_to_sleep_between_searches = st.number_input('Seconds to sleep between searches', value=1)
            slow_mo = st.number_input('Playwright slow mo', value=10)
            google_maps_query_timeout = st.number_input('Google maps query timeout', value=60000)
            headless = st.checkbox('Headless mode', value=True)

        start = st.button('Start')

    if start:
        output = st.empty()
        with st_capture(output.code):
            await start_processing_loop(
                input_file=f"{DATA_DIR}/{input_filename}",
                input_delimiter=input_delimiter,
                output_file=f"{DATA_DIR}/{output_filename}",
                output_delimiter=output_delimiter,
                slow_mo=slow_mo,
                seconds_to_sleep_between_searches=seconds_to_sleep_between_searches,
                google_maps_query_timeout=google_maps_query_timeout,
                headless=headless
            )
            st.write("Done!")
            st.write(f"Check the results in {DATA_DIR}/{output_filename}")


if __name__ == '__main__':
    if sys.platform == 'win32':
        # On Windows, the default event loop is SelectorEventLoop, which does not
        # support subprocesses. The ProactorEventLoop should be used instead.
        # Source: https://discuss.streamlit.io/t/using-playwright-with-streamlit/28380/2
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    else:
        asyncio.run(main())
