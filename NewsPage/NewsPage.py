"""This file handles the news section."""
# IMPORTS
from bs4 import BeautifulSoup
import LinkShortener
import requests
from validators import url
import webbrowser
import smtplib
import _thread

from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen


# Sends a notification email to all users
def send_email_notification(link):
    email_user = "no2.reminder@gmail.com"
    email_password = "" # TODO: Add password to field
    sent_from = email_user
    # Gets all users from th database
    users = requests.get("https://no2project.herokuapp.com/backend_api/no2_backend/users").json()
    # Creates email server to send the notifications
    server = smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(email_user,email_password)
    # Sends different email to each user in the database
    for user in users:
        if user["role"] == "user" and user["allows_email"]:
            message = f"""
                Hello {user["username"]}
                A new article has been added to the News Page
                Read it here:
                {link}"""
            server.sendmail(sent_from,user["email"],message)
    server.close()



class Article(ButtonBehavior, GridLayout):
    """Widget to display articles feed, displays an image, title and description, opens webpage when clicked on"""
    id = NumericProperty(0)
    link = StringProperty("")
    title = StringProperty("")
    desc = StringProperty("")
    img = StringProperty("")
    screen = ObjectProperty()
    pass

    # Method called when the article is clicked on
    def on_click(self, touch):
        if (self.x <= touch.x <= self.x + self.screen.width) and (self.y - 300 <= touch.y <= self.y):
            # Checks if the screen was opened from the admin screen or not
            if not self.screen.is_admin:
                self.open_link()
            else:
                popup = AdminArticlePopup()
                popup.article = self
                popup.screen = self.screen
                popup.open()

    # Method to open the articles link
    def open_link(self):
        webbrowser.open(self.link)


class ArticleList(GridLayout):
    """Grid layout to stores the list of articles"""
    pass


class AddArticlePopup(Popup):
    """Popup for the admin view of the page, allows them to add articles to the feed"""
    link_text = ObjectProperty()
    message = ObjectProperty()
    screen = ObjectProperty()
    pass

    # Adds article to the text document
    def add_article(self):
        self.message.text = ""
        link = self.link_text.text
        # Checks if the link is a real URL
        if url(link):
            exists = False
            # Shortens URL to a tinyURL to be stored in the database
            link = LinkShortener.shorten(link)
            # Checks if article is already stored in the database
            for article in requests.get('https://no2project.herokuapp.com/backend_api/no2_backend/articles').json():
                if link == article["link"]:
                    exists = True
                    break
            if not exists:
                try:
                    # Gets HTML for page
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content, "html.parser")
                    # Selects title, description and image link from the article and will fail if they cannot be found
                    title = soup.find("meta", property="og:title")["content"]
                    if len(title) > 150:
                        title = title[:145] + "..."
                    desc = soup.find("meta", property="og:description")["content"]
                    if len(desc) > 300:
                        desc = desc[:295] + "..."
                    img = soup.find("meta", property="og:image")["content"]
                    img = LinkShortener.shorten(img)
                    article = {"link": link, "title": title, "desc": desc, "image": img}
                    # Adds article to the database
                    requests.post('https://no2project.herokuapp.com/backend_api/no2_backend/create/article', data=article).json()
                except:
                    self.message.text = "Failed to add article"
                else:
                    self.message.text = "Article added successfully"
                    self.screen.update_article_list()
                    _thread.start_new_thread(send_email_notification,(link,))
            else:
                self.message.text = "Article already in database"
        else:
            self.message.text = "Invalid URL"


class AdminArticlePopup(Popup):
    """Popup for the admin view of the news page, allows them to remove articles instead of opening them"""
    article = ObjectProperty()
    screen = ObjectProperty()
    pass

    # Removes article that was clicked on from the text file
    def remove_article(self):
        requests.delete(f'https://no2project.herokuapp.com/backend_api/no2_backend/{str(self.article.id)}/delete/article').json()
        self.screen.update_article_list()
        self.dismiss()


class NewsScreen(Screen):
    """Screen to display the news articles"""
    article_list = ObjectProperty()
    add_article_button = ObjectProperty()
    is_admin = False
    pass

    # Displays the pop for adding articles
    def add_article_popup(self):
        popup = AddArticlePopup()
        popup.screen = self
        popup.open()

    # Loads news articles from the db
    def load_screen(self):
        self.update_article_list()

    # Disables the admin functionality for the news screen
    def disable_admin_functionality(self):
        self.add_article_button.disabled = True
        self.add_article_button.opacity = 0
        self.is_admin = False

    # Enables the admin functionality for the news screen
    def enable_admin_functionality(self):
        self.add_article_button.disabled = False
        self.add_article_button.opacity = 1
        self.is_admin = True

    # Updates the list of articles
    def update_article_list(self):
        self.article_list.clear_widgets()
        # Get articles from the database
        articles = requests.get('https://no2project.herokuapp.com/backend_api/no2_backend/articles').json()
        # Reverse the order so the more recent articles added are at the top
        articles.reverse()
        # Creates an article object for each row in the database
        for article in articles:
            news_article = Article()
            news_article.id = article["id"]
            news_article.link = article["link"]
            news_article.img = article["image"]
            news_article.title = article["title"]
            news_article.desc = article["desc"]
            news_article.screen = self
            self.article_list.add_widget(news_article)
        self.article_list.add_widget(
            Label(text="End of Feed", font_size='20sp', valign="top", halign="left", color=(1, 1, 1, 1)))
