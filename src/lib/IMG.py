from PIL import Image,ImageDraw,ImageFont
import requests
from io import BytesIO
from cairosvg import svg2png
import unicodedata

def remove_accents(text):
    nfkd_form = unicodedata.normalize('NFKD', text)
    only_ascii = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
    return only_ascii

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
        # Generate background
        img = Image.new(mode="RGBA", size=(700,280),color = (32,32,32))
        draw = ImageDraw.Draw(img)

        # Commented because seems weird
        # Add RootMe's logo
        # logo_rootme = Image.open('img/rootme-logo.png')
        # logo_rootme = logo_rootme.resize((120,60))
        # img.paste(logo_rootme,(570,25),logo_rootme)

        # Add RootMe's title
        title_rootme = Image.open('img/rootme-title.png')
        title_rootme = title_rootme.resize((200,50))
        img.paste(title_rootme,(490,210),title_rootme)


        # Add title
        font = ImageFont.truetype('./img/fonts/bold-marker.ttf', 40)
        draw.text((40, 20), remove_accents(title), fill="green", font=font)

        # Add challenge's name
        font = ImageFont.truetype('./img/fonts/bold-marker.ttf', 30)
        draw.text((40, 175), remove_accents(challengeName), fill="yellow", font=font)

        # Add challenge's category
        font = ImageFont.truetype('./img/fonts/bold-marker.ttf', 20)
        draw.text((100, 220), remove_accents(challengeCategory), fill="grey", font=font)

        # Add server ranking

        ##### The following code in commented because I did not found a way to retrieve all flagged challenges
        ##### without using the API, so, no way to compute the serveur ranking correctly

        # if serverRanking is not None :
        #     font = ImageFont.truetype('./img/fonts/bold-marker.ttf', 15)
        #     if serverRanking == 1 or serverRanking == "1" :
        #         serverRanking = "1er du serveur"
        #     else : 
        #         serverRanking = f"{serverRanking}eme du serveur"

        #     draw.text((40, 260), remove_accents(serverRanking), fill="grey", font=font)

        # Add username
        font = ImageFont.truetype('./img/fonts/bold-marker.ttf', 30)
        draw.text((140, 85), remove_accents(username), fill="white", font=font)

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
    img_generator = IMG()

    img = img_generator.generateImage("NOUVEAU CHALLENGE VALIDE", "Neoreo","IMG/logo/auton1.jpg",3100,"XSLT - Execution de code","Web Serveur","IMG/logo/rubon196.svg",4)

    img.show()