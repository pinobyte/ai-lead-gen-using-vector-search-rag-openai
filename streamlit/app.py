import streamlit as st
st.set_page_config(page_title="LeadMeld AI", page_icon="🚀", layout="wide")
import requests
import pandas as pd
from datetime import date
import os
from dotenv import load_dotenv
import time
from streamlit_oauth import OAuth2Component
from streamlit_cookies_controller import CookieController
import jwt

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
SEARCH_CONTACTS_URL = f"{API_BASE_URL}/api/search/"
MARKETING_RESEARCH_URL = f"{API_BASE_URL}/api/analyze/"
USER_API_URL = f"{API_BASE_URL}/api/user/usage/"
USER_REGISTER_API_URL = f"{API_BASE_URL}/api/user/register/"
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URL = os.getenv("REDIRECT_URL")
AUTH_COOKIE_KEY = os.getenv("AUTH_COOKIE_KEY")

cookieController = CookieController()

oauth = OAuth2Component(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
    token_endpoint="https://oauth2.googleapis.com/token",
    refresh_token_endpoint="https://oauth2.googleapis.com/token",
    revoke_token_endpoint="https://oauth2.googleapis.com/revoke"
)

def decode_jwt(id_token):
    try:
        payload = jwt.decode(id_token, options={"verify_signature": False})
        return payload
    except jwt.DecodeError as e:
        print(f"Decoding error: {e}")
        return None

def get_tokens():
    auth = cookieController.get(AUTH_COOKIE_KEY)
    expires_at = auth["expires_at"]
    refresh_token = auth["refresh_token"]
    if expires_at and time.time() >= expires_at:
        if refresh_token:
            refreshed = refresh_access_token(refresh_token)
            if refreshed:
                cookieController.set(AUTH_COOKIE_KEY, secure=True, max_age=3600, same_site='None', value={
                    "token": refreshed["access_token"],
                    "id_token": refreshed["id_token"],
                    "refresh_token": refresh_token,
                    "expires_at": time.time() + refreshed["expires_in"]
                })
                return refreshed["id_token"], refreshed["access_token"]
            else:
                cookieController.remove(AUTH_COOKIE_KEY)
                st.rerun()
    else:
        if "id_token" in auth:
            return auth["id_token"], auth["token"]
        return '', auth["token"]
    
def refresh_access_token(refresh_token):
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    
    response = requests.post(token_url, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return None

if not cookieController.get(AUTH_COOKIE_KEY):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔍 LeadMeld AI")
        st.text("You can Sign In using one of these options:")

        result = oauth.authorize_button(
            name="Sign In with Google",
            redirect_uri=REDIRECT_URL,
            scope="https://www.googleapis.com/auth/userinfo.email openid profile",
            key="google",
            extras_params={"prompt": "consent", "access_type": "offline"},
            use_container_width=True,
            pkce='S256'
        )

        if result:
            cookieController.set(AUTH_COOKIE_KEY, secure=True, max_age=3600, same_site='None', value={
                "token": result["token"]["access_token"],
                "id_token": result["token"]["id_token"],
                "refresh_token": result["token"]["refresh_token"],
                "expires_at": result["token"]["expires_at"]
            })

            id_token, access_token = get_tokens()
            headers = {"Authorization": f"Bearer {access_token}"}
            user = requests.get(USER_API_URL, headers=headers)
            if user.status_code == 404:
                requests.post(USER_REGISTER_API_URL, headers=headers)

            st.rerun()
else:
    auth = cookieController.get(AUTH_COOKIE_KEY)

    st.title("🔍 Lead Search & AI Analysis")

    id_token, _ = get_tokens()
    payload = decode_jwt(id_token)
    if payload and 'email' in payload:
        email = payload['email']
        st.sidebar.write(f"Welcome {email}!")
    else:
        st.sidebar.write("Welcome!")

    if st.sidebar.button("Logout"):
        cookieController.remove(AUTH_COOKIE_KEY)      
        st.rerun()

    if "search_results" not in st.session_state:
        st.session_state.search_results = None
    if "show_analysis" not in st.session_state:
        st.session_state.show_analysis = False

    tab1, tab2, tab3 = st.tabs(["📇 Contact Search", "📊 Marketing Research", "🔧 Plan & Usage"])

    st.sidebar.header("Filters")

    default_value = date(2018, 1, 1)
    selected_review_date_from = st.sidebar.date_input("Review Date (From)", default_value)

    selected_industry_names = st.sidebar.multiselect(
        "Industry", 
        [
            "Information technology", "Advertising & marketing", "Real estate", "Manufacturing", "Automotive", 
            "Supply Chain, Logistics, and Transport", "eCommerce", "Retail", "Business services", "Medical", 
            "Financial services", "Education", "Consumer products & services", "Government", "Telecommunications", 
            "Energy & natural resources", "Media", "Non-profit", "Gaming", "Utilities", "GPS, Navigation & GIS", "Other industries"
        ]
    )    

    selected_company_sizes = st.sidebar.multiselect(
        "Company Size",
        [
            "1-10 Employees",
            "11-50 Employees",
            "51-200 Employees",
            "201-500 Employees",
            "501-1,000 Employees",
            "1,001-5,000 Employees",
            "5,001-10,000 Employees",
            "10,001+ Employees"
        ])
    
    st.sidebar.markdown(
    """
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; padding: 10px; box-sizing: border-box;">
        <div style="display: flex; justify-content: flex-start; align-items: center;">
            <div style="font-size: small;">
                © 2025 Created by 
                <a href="https://pinobyte.io" target="_blank" style="text-decoration: none; color: #3366cc;">
                    PinoByte
                </a>
            </div>
                <a href="https://www.youtube.com/@pinobyte" target="_blank" style="margin-left: 10px;">
                    <img src="https://cdn-icons-png.flaticon.com/512/1384/1384060.png" alt="YouTube" width="20" height="20">
                </a>
                <a href="https://www.linkedin.com/company/pinobyte" target="_blank" style="margin-left: 10px;">
                    <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" alt="LinkedIn" width="20" height="20">
                </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True)

    with tab1:
        st.subheader("Contact Search")
        st.write("Find potential contacts based on filters and queries.")

        query = st.text_area(
            "📝 Enter your query:",
            height=100,
            placeholder="Example: Find contacts who have previously used web scraping in their applications.")

        if st.button("🔎 Search Contacts"):
            if query.strip():
                with st.spinner("Searching... Please wait"):
                    try:
                        payload = {"query": query}

                        if selected_review_date_from:
                            payload["review_date_from"] = selected_review_date_from.strftime("%Y-%m-%dT00:00:00Z")

                        if selected_industry_names:
                            payload["industries"] = selected_industry_names
                        
                        if selected_company_sizes:
                            payload["company_sizes"] = selected_company_sizes

                        _, access_token = get_tokens()
                        headers = {
                            "Authorization": f"Bearer {access_token}"
                        }

                        response = requests.post(SEARCH_CONTACTS_URL, json=payload, headers=headers)

                        if response.status_code == 200:
                            data = response.json()

                            if "response" in data and data["response"]:
                                results = data["response"]

                                if isinstance(results, list) and results:
                                    df = pd.DataFrame(results)
                                    st.session_state.search_results = df
                                    st.success("✅ Contacts found!")
                                else:
                                    st.warning("⚠️ No relevant results found.")
                            else:
                                st.warning("⚠️ No results found.")
                        else:
                            st.error(f"❌ Error: {response.status_code} - {response.text}")

                    except requests.exceptions.RequestException as e:
                        st.error(f"🌐 Network error: {str(e)}")
                    except Exception as e:
                        st.error(f"⚠️ Unexpected error: {str(e)}")
            else:
                st.warning("⚠️ Please enter a query before searching.")

        if st.session_state.search_results is not None:
            st.write("#### Contact Search Results")
            items_per_page = 25
            df = st.session_state.search_results
            total_pages = (len(df) - 1) // items_per_page + 1

            if "search_page_number" not in st.session_state:
                st.session_state.search_page_number = 0

            start_idx = st.session_state.search_page_number * items_per_page
            end_idx = start_idx + items_per_page
            current_page_df = df.iloc[start_idx:end_idx]

            st.write(f"Showing page {st.session_state.search_page_number + 1} of {total_pages}")
            st.dataframe(current_page_df, height=920, width=1500)

            space_right, main_area = st.columns([5, 1])
            with main_area:
                col_prev, col_next = st.columns([1, 1])
                with col_prev:
                    if st.button("⬅️ Prev", key="prev_page", use_container_width=True):
                        if st.session_state.search_page_number > 0:
                            st.session_state.search_page_number -= 1
                            st.rerun()
                with col_next:
                    if st.button("Next ➡️", key="next_page", use_container_width=True):
                        if st.session_state.search_page_number < total_pages - 1:
                            st.session_state.search_page_number += 1
                            st.rerun()
    with tab2:
        st.subheader("Marketing Research")
        st.write("Send queries to an AI-powered analysis system to gain insights.")

        research_query = st.text_area(
            "🔎 Enter your research query:", 
            height=100, 
            placeholder="Example: What are the major challenges faced by IT companies in customer acquisition?"
        )

        if st.button("Run Analysis"):
            if research_query.strip():
                with st.spinner("Analyzing data... Please wait"):
                    try:
                        analysis_payload = {
                            "query": research_query,
                            "review_date_from": selected_review_date_from.strftime("%Y-%m-%dT00:00:00Z") if selected_review_date_from else None,
                            "industries": selected_industry_names if selected_industry_names else None,
                            "company_sizes": selected_company_sizes if selected_company_sizes else None
                            #"project_budgets": selected_project_budgets if selected_company_sizes else None
                        }
                        _, access_token = get_tokens()
                        headers = {
                            "Authorization": f"Bearer {access_token}"
                        }

                        analysis_response = requests.post(MARKETING_RESEARCH_URL, json=analysis_payload, headers=headers)

                        if analysis_response.status_code == 200:
                            analysis_result = analysis_response.json().get("response", "No insights available.")
                            st.write("#### Insights")
                            st.write(analysis_result)
                        else:
                            st.error(f"❌ Error: {analysis_response.status_code} - {analysis_response.text}")

                    except requests.exceptions.RequestException as e:
                        st.error(f"🌐 Network error: {str(e)}")
                    except Exception as e:
                        st.error(f"⚠️ Unexpected error: {str(e)}")
            else:
                st.warning("⚠️ Please enter a query before analyzing.")

    with tab3:
        st.subheader("📊 Plan & Usage")

        _, access_token = get_tokens()
        headers = {"Authorization": f"Bearer {access_token}"}
        user = requests.get(USER_API_URL, headers=headers)

        if user.status_code == 200:
            data = user.json()
            search_tokens_allocated = data["response"]["api_tokens_search_allocated"]
            search_tokens_used = data["response"]["api_tokens_search_used"]
            search_available = search_tokens_allocated - search_tokens_used
            search_usage_percent = int((search_tokens_used / search_tokens_allocated) * 100) if search_tokens_allocated else 0

            analyze_tokens_allocated = data["response"]["api_tokens_analyze_allocated"]
            analyze_tokens_used = data["response"]["api_tokens_analyze_used"]
            analyze_available = analyze_tokens_allocated - analyze_tokens_used
            analyze_usage_percent = int((analyze_tokens_used / analyze_tokens_allocated) * 100) if analyze_tokens_allocated else 0

            col1, col2, col3 = st.columns([4, 2, 2])

            with col1:
                st.markdown(f"""
                    <div style='font-size: 22px; font-weight: 600; margin-bottom: 10px;'>
                        🔐 Contact Search Token Summary
                    </div>
                    <div style='font-size: 18px;'>
                        You’ve used <strong>{search_tokens_used}</strong> of <strong>{search_tokens_allocated}</strong> Search tokens.
                    </div>
                    <div style='margin-top: 10px;'>
                """, unsafe_allow_html=True)

                st.progress(search_usage_percent)

                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div style='font-size: 22px; font-weight: 600; margin-bottom: 10px;'>
                        🔐 Marketing Research Token Summary
                    </div>
                    <div style='font-size: 18px;'>
                        You’ve used <strong>{analyze_tokens_used}</strong> of <strong>{analyze_tokens_allocated}</strong> tokens.
                    </div>
                    <div style='margin-top: 10px;'>
                """, unsafe_allow_html=True)

                st.progress(analyze_usage_percent)

                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.metric(label="Available Contact Search Tokens", value=search_available)
            with col3:
                st.metric(label="Available Marketing Research Tokens", value=analyze_available)

            # Optional warning if usage is high
            if (search_usage_percent >= 80 and search_usage_percent < 100):
                st.warning("⚠️ You're close to your Contact Search token limit. Consider upgrading or monitoring usage.")
            if (search_usage_percent == 100):
                st.error("⚠️ You've reached your Contact Search token limit. Please upgrade a plan.")
            if (analyze_usage_percent >= 80 and analyze_usage_percent < 100):
                st.warning("⚠️ You're close to your Marketing Research token limit. Consider upgrading or monitoring usage.")
            if (analyze_usage_percent == 100):
                st.error("⚠️ You've reached your Markeing Research token limit. Please upgrade a plan.")

        else:
            st.error(f"❌ Error: {user.status_code} - {user.text}")
            
            
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)