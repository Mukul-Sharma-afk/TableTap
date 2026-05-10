[I] How TableTap Works:

1. SIGNUP - My project allows users to subscribe by signing up using either a Google account or by manually entering data into a multi-step form.
    
    a. If Google account is used -> Redirects user to complete registration form that pre-fills some data and then asks user to select a role. The role determines what business data is needed from the user. Owner role will ask the user to register a new business, whereas Manager and Staff roles will only ask to select a business from a dropdown.
    
    b. If user chooses to sign up manually, they will be taken to step 2 of the form which asks for personal details and then step 3 depending on the role as mentioned above.

2. AFTER LOGIN - 
    
    a. If user has an admin account, TableTap redirects them to the landing page with an admin dashboard button in the nav bar. This will take them to the Django Admin panel that has been customized as per the specs.

    b. If user is Owner, Manager, or Staff then TableTap takes them to the dashboard. All parts of the website can be accessed from the dashboard (Table, Menu, and Order Management).

[II] How To Fully Use TableTap:

1. Signup with a new account.

2. If logged out, log back in.

3. Add a table in Table Management -> QR code will be generated and can be viewed or downloaded.

4. Add a Menu in Menu Management.

5. Add Categories for the Menu.

6. Add Menu Items for the Categories in the Menu. (Note: Image sizes cannot be too large or we'll get a 413 Request Entity Too Large error. This is because of the upload limit set by  Nginx, and I do not want to change the config for it).

7. Enable one or more Menus in the Menu Management page.

8. Let a Customer scan the QR code for a table to access the enabled menu(s) and place an order. (Note: When an order is created, table status becomes active. It becomes inactive once order status is made completed).

9. View the order in Order Management and on the Dashboard's Recent Orders (note: Dashboard shows only limited orders, not all).

10. Use the View (eye) button to view order details and change the status of the orders from pending to in-progress to completed.

11. Visit the dashboard for business stats.


Please note: I have provided an admin and owner's credentials in the feature declaration form, but if I have made a mistake in the password (unlikely) then please feel free to create a new account for any staff member using the signup page and reach out to me to give the correct admin credentials.

[III] References:

1. Rohmad Khoirudin. (2022, June 29). Olcef – Admin Dashboard [Design showcase]. Dribble. https://dribbble.com/shots/18609074-Olcef-Admin-Dashboard?utm_source=Clipboard_Shot&utm_campaign=Rohmad_Khoir&utm_content=Olcef%20-%20Admin%20Dashboard%20%F0%9F%94%A5&utm_medium=Social_Share&utm_source=Clipboard_Shot&utm_campaign=Rohmad_Khoir&utm_content=Olcef%20-%20Admin%20Dashboard%20%F0%9F%94%A5&utm_medium=Social_Share

2. Web Dev Simplified. (2022, February 23). Can I Create This Complex Animated Multistep Form? [Video]. YouTube. https://youtu.be/VdqtdKXxKhM?si=oDRPrXit8uK7GPPx

3. Lincolnloop, maribedran, SmileyChris. (2024, October 1). QR Code image generator. PyPI. https://pypi.org/project/qrcode/

4. Tomasso, Patrick. (2018). Cozy Bar. Picture of a Cozy Bar on Unsplash. Unsplash. https://unsplash.com/photos/brown-themed-bar-GXXYkSwndP4

[IV] Acknowledgements:

ChatGPT (Free version) was used to understand how to accomplish certain things in the project.
1. ChatGPT was used to understand how to have social login mixed seemlessly into my multi-step form. In my version of TableTap (dev) when I was not using social login, I was only asking users to fill in their personal and business details. These business details are important for the dashboard and all other pages after login. When Social login is used, I do not have the business details so everything after login breaks. I referred to the lab documentation for the social signup part, but I also asked ChatGPT to explain how to redirect users to a form where user details and business information would be captured. 
2. ChatGPT helped with providing and understanding the signals.py and adapters.py files. These were not explained or taught during the labs so I was unaware of their use and purpose. 
3. ChatGPT was prompted to explain how to convert my multistep form into my view for signup. Parts of the code have been adapted from ChatGPT responses. Specifically, user backend issue occurred when social login was added to the code, and ChatGPT assisted with understanding the problem and then providing potential fixes. The fix was adapted from ChatGPT's response.
4. ChatGPT and QR code documentation was used to allow QR code generation. The reason for putting the code in utils.py was understood using ChatGPT - the reason being that views.py should ideally handle only user requests and responses, and generate_qr_code() is busness logic.
5. Acknowledgements from the design document assignment are appropriate for this submission as well because I have ported my html mockups into the templates. The acknowledgement was as follows: I acknowledge the use of Generative AI (ChatGPT & DallE) in making the images for this document and for the HTML mockups that contain images. Generative AI was also used to help fix errors with the JavaScript in the modal of the order management page and for fixing some of the custom styles in the css based on how I envisioned the elements to look. Please note that I have not used any AI generated images from DallE for the website (They were only used in the mockups).
6. I would also like to acknowledge the use of the Resumebuilder Lab work for building a base for the project and certain parts of the project. Additionally, the admin dashboard was created based on the documentation provided in the lab work.