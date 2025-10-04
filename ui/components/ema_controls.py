import streamlit as st

class EMAControls:
    """UI component for EMA (Exponential Moving Average) controls"""

    @staticmethod
    def render(on_change_callback=None):
        """
        Render EMA controls panel

        Args:
            on_change_callback: Function to call when EMA settings change

        Returns:
            None (modifies session state directly)
        """
        st.markdown(
            "<div style='background-color:#e3e6ea;padding:10px 0 10px 0;margin-bottom:10px;'>"
            "<b>Indicators: Exponential Moving Average (EMA)</b>",
            unsafe_allow_html=True
        )

        # Ensure EMA list exists in session state
        if 'ema_list' not in st.session_state:
            st.session_state['ema_list'] = [{'period': 20, 'visible': True}]

        ema_cols = st.columns([2, 2, 2, 2, 2])

        # Render EMA controls
        for i, ema in enumerate(st.session_state['ema_list']):
            unique_key = f"{i}_{id(ema)}"
            with ema_cols[i % 5]:
                # Period input
                new_period = st.number_input(
                    f"EMA {i+1} Period",
                    min_value=1,
                    max_value=200,
                    value=ema['period'],
                    key=f"ema_period_{unique_key}",
                    on_change=on_change_callback
                )
                st.session_state['ema_list'][i]['period'] = new_period

                # Visibility checkbox
                new_visible = st.checkbox(
                    f"Show EMA {i+1}",
                    value=ema['visible'],
                    key=f"ema_visible_{unique_key}",
                    on_change=on_change_callback
                )
                st.session_state['ema_list'][i]['visible'] = new_visible

        # Add/Remove buttons
        col1, col2 = st.columns(2)
        with col1:
            def add_ema_handler():
                EMAControls.add_ema()
                if on_change_callback:
                    on_change_callback()

            st.button("Add EMA", key="add_ema_btn", on_click=add_ema_handler)

        with col2:
            def remove_ema_handler():
                EMAControls.remove_ema()
                if on_change_callback:
                    on_change_callback()

            st.button("Remove Last EMA", key="remove_ema_btn", on_click=remove_ema_handler)

        st.markdown("</div>", unsafe_allow_html=True)

    @staticmethod
    def add_ema():
        """Add a new EMA to the list"""
        if 'ema_list' not in st.session_state:
            st.session_state['ema_list'] = []
        st.session_state['ema_list'].append({'period': 20, 'visible': True})

    @staticmethod
    def remove_ema():
        """Remove the last EMA from the list"""
        if 'ema_list' in st.session_state and len(st.session_state['ema_list']) > 1:
            st.session_state['ema_list'].pop()

    @staticmethod
    def get_ema_list():
        """Get the current EMA list from session state"""
        return st.session_state.get('ema_list', [{'period': 20, 'visible': True}])

    @staticmethod
    def get_visible_emas():
        """Get only the visible EMAs"""
        ema_list = EMAControls.get_ema_list()
        return [ema for ema in ema_list if ema.get('visible', False)]

    @staticmethod
    def render_simple(key_suffix=""):
        """
        Render simplified EMA controls (for app.py compatibility)

        Args:
            key_suffix: Suffix to add to component keys for uniqueness
        """
        st.markdown(
            "<div style='background-color:#e3e6ea;padding:10px 0 10px 0;margin-bottom:10px;'>"
            "<b>Indicators: Exponential Moving Average (EMA)</b>",
            unsafe_allow_html=True
        )

        if 'ema_list' not in st.session_state:
            st.session_state['ema_list'] = [{'period': 20, 'visible': True}]

        def refresh_chart_on_ema_toggle():
            st.session_state['show_chart_auto'] = True

        ema_cols = st.columns([2, 2, 2, 2, 2])

        for i, ema in enumerate(st.session_state['ema_list']):
            with ema_cols[i % 5]:
                st.session_state['ema_list'][i]['period'] = st.number_input(
                    f"EMA {i+1} Period",
                    min_value=1,
                    max_value=200,
                    value=ema['period'],
                    key=f"ema_period_{i}{key_suffix}"
                )
                st.session_state['ema_list'][i]['visible'] = st.checkbox(
                    f"Show EMA {i+1}",
                    value=ema['visible'],
                    key=f"ema_visible_{i}{key_suffix}",
                    on_change=refresh_chart_on_ema_toggle
                )

        def add_ema_simple():
            st.session_state['ema_list'].append({'period': 20, 'visible': True})
            st.session_state['show_chart_auto'] = True

        def remove_ema_simple():
            if len(st.session_state['ema_list']) > 1:
                st.session_state['ema_list'].pop()
                st.session_state['show_chart_auto'] = True

        st.button("Add EMA", key=f"add_ema_btn{key_suffix}", on_click=add_ema_simple)
        st.button("Remove Last EMA", key=f"remove_ema_btn{key_suffix}", on_click=remove_ema_simple)

        st.markdown("</div>", unsafe_allow_html=True)