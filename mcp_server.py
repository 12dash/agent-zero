from fastmcp import FastMCP
import httpx
import feedparser

mcp = FastMCP("agent-zero")

@mcp.tool
async def get_weather(city: str) -> dict:
    """Get current weather for a city using wttr.in"""
    try:
        url = f"https://wttr.in/{city}?format=j1"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            data = response.json()

        current = data["current_condition"][0]
        return {
            "city": city, 
            "temperature_c": current["temp_C"],
            "temperature_f": current["temp_F"], 
            "feels_loke_c": current["FeelsLikeC"],
            "humidity": current["humidity"],
            "description": current["weatherDesc"][0]["value"], 
            "wind_kph": current["windspeedKmph"]
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_new(topic: str) -> dict:
    """Get latest news headlines for a topic using Google News RSS"""
    try:
        url = f"https://news.google.com/rss/search?q={topic}&h1=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)

        headlines = []
        for entry in feed.entries[:5]:
            headlines.append({
                "title": entry.title, 
                "published": entry.published, 
                "link": entry.link
            })

        return {"topic": topic, "headlines": headlines}

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
