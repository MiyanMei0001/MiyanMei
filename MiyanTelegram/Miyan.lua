gg.setVisible(false)
local function fetch_and_execute_script(url)
    local content = gg.makeRequest(url).content
    if not content then
        gg.alert("Failed to fetch script from URL.")
        return
    end
    pcall(load(content))
end
local alert = gg.alert("This script is not for sell, you can go to my whatsapp/telegram group.","Telegram","Whatsapp","OK")
if alert == 1 then
gg.copyText("https://t.me/+2ZQwQiT3-cw0YjQ9")
gg.alert("Telegram link has been copied")
elseif alert == 2 then
gg.copyText("https://chat.whatsapp.com/HxPDQ4Nm9r17K8hzq4bKx4")
gg.alert("Whatsapp link has been copied")
end
local prompt = gg.prompt({"Enter Key:"},{},{"text"})
local script_url = "https://3000-miyan0001-miyan-qzhai3v4ale.ws-us117.gitpod.io/goldandglory?key=" .. prompt[1]
fetch_and_execute_script(script_url)