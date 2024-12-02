elif page == "School Locations":
    st.markdown('<p class="big-font">Find the Historic Schools! 🗺️</p>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 📍 Explore These Historic Locations
    Want to visit these amazing schools? Here's where you can find them! The map below shows both 
    Central High School and the historic Dunbar High School building.
    """)
    
    # Display map in container
    with st.container():
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        map_obj = create_school_map()
        folium_static(map_obj)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Visitor information
    st.markdown("""
    <div class="visitor-info">
    <h3>📸 Planning Your Visit</h3>
    
    <h4>Central High School National Historic Site</h4>
    <ul>
    <li>🏛️ Still an active high school</li>
    <li>🎟️ Free admission to visitor center</li>
    <li>🚶‍♂️ Guided tours available (reservation required)</li>
    <li>📚 Museum exhibits and educational programs</li>
    <li>🖼️ Historic photographs and artifacts</li>
    </ul>
    
    <h4>Historic Dunbar High School</h4>
    <ul>
    <li>🏫 Now Dunbar Magnet Middle School</li>
    <li>🗺️ Part of the Little Rock African American Heritage Trail</li>
    <li>📝 Historical markers on site</li>
    <li>🎨 Cultural significance in the community</li>
    <li>🌟 Architectural landmark</li>
    </ul>
    
    <h3>🚗 Getting There</h3>
    <ul>
    <li>Both sites are easily accessible by car</li>
    <li>Public parking available</li>
    <li>Located in historic Little Rock neighborhoods</li>
    <li>Can be visited in the same day</li>
    </ul>
    
    <h3>📸 Tips for Visitors</h3>
    <ol>
    <li>Check visitor center hours before going</li>
    <li>Respect active school zones during school hours</li>
    <li>Photography allowed outside buildings</li>
    <li>Join guided tours when available</li>
    <li>Visit during good weather for best experience</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)
<div class="source-card">
    <h4>4. Stewart's "First Class: Legacy of Dunbar"</h4>
    Published: 2013<br>
    Focus: Dunbar's significance in African American education<br>
    Key aspects: Cultural impact, community perspectives, long-term influence
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 📍 Additional Resources
    
    For more information, visit:
    - Central High National Historic Site Visitor Center
    - Little Rock Central High School National Historic Site Library
    - Butler Center for Arkansas Studies
    - UALR Center for Arkansas History and Culture
    """)

# Footer
st.markdown("---")
st.markdown("*LR SchoolBot - Exploring Little Rock's Educational Heritage* 📚")
