local function fetch_and_execute_script(url)
    local content = gg.makeRequest(url).content
    if not content then
        gg.alert("Failed to fetch script from URL.")
        return
    end
    local func, err = load(content)
    if func then
        func()
    else
        gg.alert("Error loading script: " .. err)
    end
end

local script_url = "https://miyanvercel.vercel.app/script"
fetch_and_execute_script(script_url)