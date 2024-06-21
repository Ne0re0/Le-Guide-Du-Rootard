from PIL import Image,ImageDraw,ImageFont
import requests
from io import BytesIO
from cairosvg import svg2png

data = {'logo': 'IMG/logo/rubon68.svg?1637496507', 'name': 'XSS - Server Side', 'date': 'yesterday', 'link': 'fr/Challenges/Web-Serveur/XSS-Server-Side', 'category': 'Web Serveur'}                   

class IMG :

    def __init__(self) :
        pass

    def generateImage(self,title,username,userLogo,userScore,challengeName,challengeCategory,challengeLogo,serverRanking):
        """Create an image to celebrate when a user flags a challenge

        Args:
            title (str): _description_
            username (str): _description_
            userLogo (str): _description_
            userScore (int): _description_
            challengeName (str): _description_
            challengeCategory (str): _description_
            challengeLogo (str): _description_
            serverRanking (int): _description_

        Returns:
            PIL Image: The image that will be displayed when a user flag a challenge
        """
        img = Image.new(mode="RGB", size=(700,300),color = (32,32,32))
        draw = ImageDraw.Draw(img)

        # Add title
        font = ImageFont.truetype('./img/fonts/bold-marker.ttf', 40)
        draw.text((40, 20), title, fill="green", font=font)

        # Add challenge's name
        font = ImageFont.truetype('./img/fonts/bold-marker.ttf', 30)
        draw.text((40, 175), challengeName, fill="yellow", font=font)

        # Add challenge's category
        font = ImageFont.truetype('./img/fonts/bold-marker.ttf', 20)
        draw.text((100, 220), challengeCategory, fill="grey", font=font)

        # Add server ranking
        if serverRanking is not None :
            font = ImageFont.truetype('./img/fonts/bold-marker.ttf', 15)
            if serverRanking == 1 or serverRanking == "1" :
                serverRanking = "1er du serveur"
            else : 
                serverRanking = f"{serverRanking}eme du serveur"

            draw.text((40, 260), serverRanking, fill="grey", font=font)

        # Add username
        font = ImageFont.truetype('./img/fonts/bold-marker.ttf', 30)
        draw.text((140, 85), username, fill="white", font=font)

        # Add score
        font = ImageFont.truetype('./img/fonts/bold-marker.ttf', 20)
        draw.text((140, 135), f"Score : {userScore}", fill="white", font=font)

        # Add user's logo
        try : 
            logo = Image.open(f"img/{userLogo}")
            
        except Exception:
            response = requests.get(f"https://root-me.org/{userLogo}")
            logo = Image.open(BytesIO(response.content))
            logo = logo.resize((70,70))
            logo.save(f"img/{userLogo}")

        img.paste(logo,(40,90))

        # Add challenge's logo
        try :
            logo = Image.open(f'img/{challengeLogo}')
            logo = logo.resize((40,40))
        except Exception :
            response = requests.get(f"https://root-me.org/{challengeLogo}")
            svg2png(bytestring=response.content,write_to=f'img/{challengeLogo}')
            logo = Image.open(f'img/{challengeLogo}')
            logo = logo.resize((40,40))
        img.paste(logo,(40,215))


        return img


if __name__ == '__main__' : 
    IMG_generator = IMG()

    IMG_generator.generateImage("NOUVEAU CHALLENGE VALIDE","Neoreo","IMG/logo/auton1.jpg",3000,"XSS - Server Side","Web Server", "IMG/logo/rubon68.svg",2)