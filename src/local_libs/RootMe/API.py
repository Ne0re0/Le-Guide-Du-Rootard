import requests
from bs4 import BeautifulSoup
from local_libs.RootMe.UserAgents import UserAgents

class API :

    def __init__(self) : 
        self.ua_generator = UserAgents("./ressources/user-agents.txt")

    def getUser(self,username) :
        """Returns the user's informations

        Args:
            username (string): the username

        Raises:
            Exception: Id the username does not exists

        Returns:
            dict: the user's informations 
        """
        headers = {"User-Agent":self.ua_generator.getRandom()}
        try :
            resp = requests.get(f"https://www.root-me.org/{username}?&lang=en&debut_ao=0&debut_challenges_auteur=0&debut_articles_auteur=0",headers=headers, timeout=10)
            if resp.status_code != 200 :
                return {"status_code":resp.status_code,"url":f"https://www.root-me.org/{username}?&lang=en"}
            soup = BeautifulSoup(resp.text, 'html.parser')
            data = {}
            data["username"] = self.__getUsername(soup)
            data['points'] = self.__getPoints(soup)
            data['position'] = self.__getPosition(soup)
            data['flagNumber'] = self.__getFlagNumber(soup)
            data['profilePicture'] = self.__getProfilePicture(soup)
            data['biography'] = self.__getBiography(soup)
            data['compromissionNumber'] = self.__getCompromissionNumber(soup)
            data['recentActivity'] = self.__getRecentActivity(soup)
            data['validations'] = self.__getValidations(soup)
            data['badges'] = self.__getBadges(soup)
            data['contributions'] = self.__getContributions(soup)
            return data

        except requests.exceptions.Timeout:
            return {"status_code":"Timeout","url":f"https://www.root-me.org/{username}?&lang=en"}
        except Exception :
            return {"status_code":"Error","url":f"https://www.root-me.org/{username}?&lang=en"}

    def __getUsername(self,soup) :
        """Returns the username"""
        repere = soup.find("h1",{"itemprop":"givenName"})
        username = repere.find("span").getText()
        return username

    def __getPoints(self,soup) :
        """Returns the number of points"""
        repere = soup.find("img",{"src":"squelettes/img/valid.svg?1566650916","width":"24"})
        points = repere.findParent().getText()
        return int(points)

    def __getPosition(self,soup) :
        """Returns the global position in the scoreboard"""
        repere = soup.find("img",{"src":"squelettes/img/classement.svg?1647504561","width":"24"})
        position = repere.findParent().getText()
        return int(position)

    def __getFlagNumber(self,soup) :
        """Returns the number of flagged challenges"""
        repere = soup.find("img",{"src":"IMG/logo/rubon5.svg?1637496507","width":"24"})
        flagNumber = repere.findParent().getText()
        return int(flagNumber)

    def __getProfilePicture(self,soup) :
        """Returns the link to the profile picture"""
        repere = soup.find("h1",{"itemprop":"givenName"})
        img = repere.find("img")
        return img["src"]

    def __getBiography(self,soup) :
        """Returns the biography"""
        try :
            repere = soup.find("li",{"itemprop":"description"})
            biography = repere.find_next("p").getText()
            return biography
        except Exception: 
            return ''

    def __getCompromissionNumber(self,soup) :
        """Returns the number of compromissions"""
        repere = soup.find("img",{"src":"IMG/logo/rubon196.svg?1637496499","width":"24"})
        compromissionNumber = repere.findParent().getText()
        return int(compromissionNumber)

    def __getRecentActivity(self,soup) :
        """Returns the last 10 solved challenges"""
        try :
            img_tag = soup.find('img', {'src': 'squelettes/img/activitees.svg?1570951387',"width":"32"})
            challenges = img_tag.find_next('ul').children
            challenges = [chall for chall in challenges if "li" in f"{chall}"]
            data = []
            for i,challenge in enumerate(challenges) : 
                data.append({})
                data[i]["logo"] = challenge.find("img")['src']
                data[i]["name"] = challenge.find("a").getText()
                data[i]["date"] = challenge.find("span").getText()
                data[i]["link"] = challenge.find("a")["href"]
                data[i]["category"] = " ".join(data[i]["link"].split("/")[2].split("-"))

            return data
        except :
            return []

    def __getValidations(self,soup) :
        """Returns the percentage of solves challenges from the different categories"""
        validations = {"total":{},"details": []}
        repere = soup.find("img",{"src":"squelettes/img/valid.svg?1566650916","width":"32"}).findParent().findParent()
        children = [child for child in repere.children if "div" in f"{child}"]
        for i,child in enumerate(children[:-1]) : 
            validations['details'].append({})
            validations['details'][i]["logo"] = child.find("span")["style"].split("url(")[1].split(")")[0]
            validations['details'][i]["title"] = " ".join(child.find("a")["href"].split("/")[2].split("-"))
            validations['details'][i]["link"] = child.find("a")["href"]
            validations['details'][i]["percent"] = child.find("a").getText()

        validations['total']['percent'] = children[-1].find("h3").getText().split("%")[0] + "%"
        validations['total']['flaggedChallenges'] = int(children[-1].find("h3").getText().split("%")[1].split("/")[0])
        validations['total']['totalChallenges'] = int(children[-1].find("h3").getText().split("%")[1].split("/")[1])

        return validations

    def __getBadges(self,soup) :
        """Returns all the badges owned"""
        try :
            badges = []
            repere = soup.find_all(lambda tag: tag.name == "h3" and "Badges" in tag.text)[0].findParent()
            children = [child for child in repere.children if "span" in f"{child}"]
            for i,child in enumerate(children) :
                badges.append({}) 
                badges[i]["background"] = child.find("span",{"class":"vmiddle text-center"})['style'].split("url('")[1].split("')")[0]
                try :
                    badges[i]["logo"] = child.find("img")["src"]
                    badges[i]["title"] = child.find("img")["title"]
                except Exception :
                    pass            
            return badges
        except Exception : 
            return []
    
    def __getContributions(self,soup) :
        """Return contributions such as challenges and challenges write-ups"""
        contributions = {"challenges":[],"solutions":[]}

        repere = soup.find("img",{"src":"IMG/logo/rubon175.svg?1637496498","height":"32","width":"32"}).findParent().findParent().findParent().findNextSibling()

        try :
            repereChallenges = repere.find("h4").findNext("ul")
            children = [child for child in repereChallenges.children if "li" in f"{child}"]
            for i,child in enumerate(children) :
                contributions['challenges'].append({})
                contributions['challenges'][i]['logo'] = child.find("img")["src"]
                contributions['challenges'][i]['title'] = child.find("img").findNext("a").getText()
                contributions['challenges'][i]['link'] = child.find("img").findNext("a")["href"]
                contributions['challenges'][i]['category'] = " ".join(contributions['challenges'][i]['link'].split("/")[2].split("-"))
        except Exception :
            pass

        try :
            repereSolutions = repere.findNextSibling().find("h4").findNext("ul")
            children = [child for child in repereSolutions.children if "li" in f"{child}"]

            for i,child in enumerate(children) : 
                contributions['solutions'].append({})
                contributions['solutions'][i]['logo'] = child.find("img")["src"]
                contributions['solutions'][i]['title'] = child.find("img").findNext("a").getText()
                contributions['solutions'][i]['link'] = child.find("img").findNext("a")["href"]
                contributions['solutions'][i]['category'] = " ".join(contributions['solutions'][i]['link'].split("/")[2].split("-"))
        
        except Exception :
            pass

        return contributions


if __name__ == '__main__' : 
    api = API()
    print(api.getUser("g0uZ"))


