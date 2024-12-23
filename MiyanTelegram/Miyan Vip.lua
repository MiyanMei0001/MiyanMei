local function find_library_base(lib_name, state_filter)
    local ranges = gg.getRangesList(lib_name)
    for _, range in ipairs(ranges) do
        if range.state == state_filter then
            return range.start
        end
    end
    gg.alert("Library not found or matching state not available")
    return nil
end

local function generate_method_table(lib_base, method)
    local t = {}
    local values = type(method.value) == "table" and method.value or {method.value}

    for i, offset in ipairs(method.offsets) do
        local value = values[i] or values[#values]
        table.insert(t, {
            address = lib_base + offset,
            flags = 32,
            value = "h" .. value,
            name = method.name
        })
    end

    return t
end

local target_info = gg.getTargetInfo()
local is64bit = target_info.x64
local arch = is64bit and "64-bit" or "32-bit"
gg.toast("Detected architecture: " .. arch)

local lib_name = "libil2cpp.so"
local lib_base = find_library_base(lib_name, "Xa")
if not lib_base then return end

local method_list_64bit = {
    {name = "Unlimited Jump", offsets = {0x1b8af40}, value = "E0CF8952C0035FD6"},
    {name = "Equip All Armor", offsets = {0x1c83178}, value = "200080D2C0035FD6"},
    {name = "Use Skill Without Weapon", offsets = {0x1c722a8}, value = "200080D2C0035FD6"},
    {name = "See Items Color in Chest", offsets = {0x1b9389c}, value = "200080D2C0035FD6"},
    {name = "Skip Search Loot", offsets = {0x1c869e8}, value = "200080D2C0035FD6"},
    {name = "Attack Team", offsets = {0x1bae180}, value = "000080D2C0035FD6"},
    {name = "Can See Rogue Stealth", offsets = {0x200adec}, value = "C0035FD6"},
    {name = "Can through Players or Monsters", offsets = {0x1B86A78, 0x1B9A6E8}, value = "200080D2C0035FD6"},
    {name = "Can see Pain Warden chest (Activate In Red Portal Lobby)", offsets = {0x2010DD8, 0x2011B48}, value = "000080D2C0035FD6"},
    {name = "Increase Attack & Skill Speed 2x", offsets = {0x1ba1150, 0x1ba1150 + 8, 0x1ba1150 + 12}, value = {"400080520000271E","00D8215E0000261E","C0035FD609102E1E"}},
    {name = "Increase Attack & Skill Speed 3x", offsets = {0x1ba1150, 0x1ba1150 + 8, 0x1ba1150 + 12}, value = {"600080520000271E","00D8215E0000261E","C0035FD609102E1E"}},
}

local method_list_32bit = {
    {name = "Unlimited Jump", offsets = {0x2b63984}, value = "0F0702E31EFF2FE1"},
    {name = "Equip All Armor", offsets = {0x2c9ad38}, value = "0100A0E31EFF2FE1"},
    {name = "Use Skill Without Weapon", offsets = {0x2c84bc0}, value = "0100A0E31EFF2FE1"},
    {name = "See Items Color in Chest", offsets = {0x2b6e30c}, value = "0100A0E31EFF2FE1"},
    {name = "Skip Search Loot", offsets = {0x2c9f688}, value = "0100A0E31EFF2FE1"},
    {name = "Attack Team", offsets = {0x2b8e77c}, value = "0000A0E31EFF2FE1"},
    {name = "Can See Rogue Stealth", offsets = {0x312a960}, value = "1EFF2FE1"},
    {name = "Increase Attack & Skill Speed 2x", offsets = {0x2b7e4ec}, value = "000044E31EFF2FE1E1"},
    {name = "Increase Attack & Skill Speed 3x", offsets = {0x2b7e4ec}, value = "400044E31EFF2FE1E1"},
}

local method_list = is64bit and method_list_64bit or method_list_32bit

local method_status = {}
local original_values = {}

for _, method in ipairs(method_list) do
    method_status[method.name] = false
    original_values[method.name] = {}
end

local function show_menu()
    local choices = {}
    local default_choices = {}

    for i, method in ipairs(method_list) do
        table.insert(choices, method.name .. (method_status[method.name] and " [🔵]" or " [🔴]"))
        table.insert(default_choices, method_status[method.name])
    end

    local selected = gg.multiChoice(choices, nil, "Ｍｉｙａｎ VIP")

    if selected then
        for i, _ in pairs(selected) do
            local method_table = generate_method_table(lib_base, method_list[i])
            if method_status[method_list[i].name] then
                gg.setValues(original_values[method_list[i].name])
                gg.toast(method_list[i].name .. " disabled")
            else
                for _, entry in ipairs(method_table) do
                    table.insert(original_values[method_list[i].name], gg.getValues({entry})[1])
                end
                gg.setValues(method_table)
                gg.toast(method_list[i].name .. " enabled")
            end
            method_status[method_list[i].name] = not method_status[method_list[i].name]
        end
    else
        gg.toast("No feature selected")
    end
end

while true do
    if gg.isVisible(true) then
        gg.setVisible(false)
        show_menu()
    end
gg.sleep(1000)
end