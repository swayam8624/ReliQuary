#define GLFW_INCLUDE_VULKAN
#include <GLFW/glfw3.h>

#include <curl/curl.h>
#include <imgui.h>
#include <backends/imgui_impl_glfw.h>
#include <backends/imgui_impl_vulkan.h>
#include <nlohmann/json.hpp>

#include <algorithm>
#include <array>
#include <cstring>
#include <iostream>
#include <functional>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

using json = nlohmann::json;

namespace {

constexpr uint32_t WIDTH = 1440;
constexpr uint32_t HEIGHT = 900;

struct QueueFamilyIndices {
    std::optional<uint32_t> graphicsFamily;
    std::optional<uint32_t> presentFamily;
    bool complete() const { return graphicsFamily.has_value() && presentFamily.has_value(); }
};

struct ApiState {
    std::string apiUrl = "http://localhost:8000";
    std::string owner = "alice";
    std::string vaultName = "brain-vault";
    std::string vaultId;
    std::string secretName = "apple-password-note";
    std::string secretValue = "replace-with-a-real-secret";
    std::string secretPassword = "specific-password";
    std::string filePath;
    std::string sharePassword = "share-pass";
    std::string shareToken;
    std::string requestUser = "alice";
    std::string remoteAddress = "127.0.0.1";
    std::string sensitivity = "secret";
    int trustScore = 95;
    bool deviceVerified = true;
    bool localSession = true;
    bool biometricVerified = true;
    std::string chatInput = "ask brain vault for apple-password-note";
    std::vector<std::string> log = {"ReliQuary ImGui console ready."};
    json lastDecision = json::object();
};

size_t writeCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    auto* buffer = static_cast<std::string*>(userp);
    buffer->append(static_cast<char*>(contents), size * nmemb);
    return size * nmemb;
}

std::string postJson(const std::string& url, const json& payload) {
    CURL* curl = curl_easy_init();
    if (!curl) throw std::runtime_error("curl_easy_init failed");
    std::string response;
    struct curl_slist* headers = nullptr;
    headers = curl_slist_append(headers, "Content-Type: application/json");
    std::string body = payload.dump();
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, body.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 8L);
    CURLcode code = curl_easy_perform(curl);
    long status = 0;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &status);
    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);
    if (code != CURLE_OK) throw std::runtime_error(curl_easy_strerror(code));
    if (status < 200 || status >= 300) {
        throw std::runtime_error("HTTP " + std::to_string(status) + ": " + response);
    }
    return response;
}

std::string getJson(const std::string& url) {
    CURL* curl = curl_easy_init();
    if (!curl) throw std::runtime_error("curl_easy_init failed");
    std::string response;
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 8L);
    CURLcode code = curl_easy_perform(curl);
    long status = 0;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &status);
    curl_easy_cleanup(curl);
    if (code != CURLE_OK) throw std::runtime_error(curl_easy_strerror(code));
    if (status < 200 || status >= 300) {
        throw std::runtime_error("HTTP " + std::to_string(status) + ": " + response);
    }
    return response;
}

std::vector<const char*> requiredInstanceExtensions() {
    uint32_t glfwCount = 0;
    const char** glfwExtensions = glfwGetRequiredInstanceExtensions(&glfwCount);
    std::vector<const char*> extensions(glfwExtensions, glfwExtensions + glfwCount);
    extensions.push_back(VK_KHR_PORTABILITY_ENUMERATION_EXTENSION_NAME);
    return extensions;
}

bool deviceSupports(VkPhysicalDevice device, const char* extensionName) {
    uint32_t count = 0;
    vkEnumerateDeviceExtensionProperties(device, nullptr, &count, nullptr);
    std::vector<VkExtensionProperties> extensions(count);
    vkEnumerateDeviceExtensionProperties(device, nullptr, &count, extensions.data());
    return std::any_of(extensions.begin(), extensions.end(), [&](const auto& ext) {
        return std::strcmp(ext.extensionName, extensionName) == 0;
    });
}

QueueFamilyIndices queueFamilies(VkPhysicalDevice device, VkSurfaceKHR surface) {
    QueueFamilyIndices indices;
    uint32_t count = 0;
    vkGetPhysicalDeviceQueueFamilyProperties(device, &count, nullptr);
    std::vector<VkQueueFamilyProperties> families(count);
    vkGetPhysicalDeviceQueueFamilyProperties(device, &count, families.data());
    for (uint32_t i = 0; i < count; ++i) {
        if (families[i].queueFlags & VK_QUEUE_GRAPHICS_BIT) indices.graphicsFamily = i;
        VkBool32 present = false;
        vkGetPhysicalDeviceSurfaceSupportKHR(device, i, surface, &present);
        if (present) indices.presentFamily = i;
    }
    return indices;
}

uint32_t memoryType(VkPhysicalDevice device, uint32_t typeFilter, VkMemoryPropertyFlags properties) {
    VkPhysicalDeviceMemoryProperties memProperties;
    vkGetPhysicalDeviceMemoryProperties(device, &memProperties);
    for (uint32_t i = 0; i < memProperties.memoryTypeCount; i++) {
        if ((typeFilter & (1 << i)) && (memProperties.memoryTypes[i].propertyFlags & properties) == properties) return i;
    }
    throw std::runtime_error("No suitable memory type");
}

class VulkanImGuiApp {
public:
    void run() {
        initWindow();
        initVulkan();
        initImGui();
        mainLoop();
        cleanup();
    }

private:
    GLFWwindow* window = nullptr;
    VkInstance instance = VK_NULL_HANDLE;
    VkSurfaceKHR surface = VK_NULL_HANDLE;
    VkPhysicalDevice physicalDevice = VK_NULL_HANDLE;
    VkDevice device = VK_NULL_HANDLE;
    VkQueue graphicsQueue = VK_NULL_HANDLE;
    VkQueue presentQueue = VK_NULL_HANDLE;
    VkSwapchainKHR swapchain = VK_NULL_HANDLE;
    VkFormat swapchainFormat = VK_FORMAT_B8G8R8A8_UNORM;
    VkExtent2D swapchainExtent{};
    VkRenderPass renderPass = VK_NULL_HANDLE;
    VkCommandPool commandPool = VK_NULL_HANDLE;
    VkDescriptorPool descriptorPool = VK_NULL_HANDLE;
    std::vector<VkImage> swapchainImages;
    std::vector<VkImageView> imageViews;
    std::vector<VkFramebuffer> framebuffers;
    std::vector<VkCommandBuffer> commandBuffers;
    std::vector<VkSemaphore> imageAvailable;
    std::vector<VkSemaphore> renderFinished;
    std::vector<VkFence> inFlight;
    size_t currentFrame = 0;
    ApiState api;

    void initWindow() {
        if (!glfwInit()) throw std::runtime_error("glfwInit failed");
        glfwWindowHint(GLFW_CLIENT_API, GLFW_NO_API);
        window = glfwCreateWindow(WIDTH, HEIGHT, "ReliQuary Brain Vault", nullptr, nullptr);
        if (!window) throw std::runtime_error("glfwCreateWindow failed");
    }

    void initVulkan() {
        VkApplicationInfo appInfo{};
        appInfo.sType = VK_STRUCTURE_TYPE_APPLICATION_INFO;
        appInfo.pApplicationName = "ReliQuary Brain Vault";
        appInfo.apiVersion = VK_API_VERSION_1_1;

        auto extensions = requiredInstanceExtensions();
        VkInstanceCreateInfo createInfo{};
        createInfo.sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO;
        createInfo.pApplicationInfo = &appInfo;
        createInfo.enabledExtensionCount = static_cast<uint32_t>(extensions.size());
        createInfo.ppEnabledExtensionNames = extensions.data();
        createInfo.flags = VK_INSTANCE_CREATE_ENUMERATE_PORTABILITY_BIT_KHR;
        if (vkCreateInstance(&createInfo, nullptr, &instance) != VK_SUCCESS) throw std::runtime_error("vkCreateInstance failed");
        if (glfwCreateWindowSurface(instance, window, nullptr, &surface) != VK_SUCCESS) throw std::runtime_error("surface failed");
        pickDevice();
        createDevice();
        createSwapchain();
        createRenderPass();
        createFramebuffers();
        createCommandPool();
        createSync();
    }

    void pickDevice() {
        uint32_t count = 0;
        vkEnumeratePhysicalDevices(instance, &count, nullptr);
        std::vector<VkPhysicalDevice> devices(count);
        vkEnumeratePhysicalDevices(instance, &count, devices.data());
        for (auto candidate : devices) {
            if (queueFamilies(candidate, surface).complete() && deviceSupports(candidate, VK_KHR_SWAPCHAIN_EXTENSION_NAME)) {
                physicalDevice = candidate;
                return;
            }
        }
        throw std::runtime_error("No Vulkan device with swapchain support found");
    }

    void createDevice() {
        auto indices = queueFamilies(physicalDevice, surface);
        std::vector<uint32_t> unique = {indices.graphicsFamily.value()};
        if (indices.presentFamily.value() != indices.graphicsFamily.value()) unique.push_back(indices.presentFamily.value());
        float priority = 1.0f;
        std::vector<VkDeviceQueueCreateInfo> queues;
        for (uint32_t family : unique) {
            VkDeviceQueueCreateInfo queueInfo{};
            queueInfo.sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO;
            queueInfo.queueFamilyIndex = family;
            queueInfo.queueCount = 1;
            queueInfo.pQueuePriorities = &priority;
            queues.push_back(queueInfo);
        }
        std::vector<const char*> extensions = {VK_KHR_SWAPCHAIN_EXTENSION_NAME};
        if (deviceSupports(physicalDevice, "VK_KHR_portability_subset")) extensions.push_back("VK_KHR_portability_subset");
        VkDeviceCreateInfo info{};
        info.sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO;
        info.queueCreateInfoCount = static_cast<uint32_t>(queues.size());
        info.pQueueCreateInfos = queues.data();
        info.enabledExtensionCount = static_cast<uint32_t>(extensions.size());
        info.ppEnabledExtensionNames = extensions.data();
        if (vkCreateDevice(physicalDevice, &info, nullptr, &device) != VK_SUCCESS) throw std::runtime_error("vkCreateDevice failed");
        vkGetDeviceQueue(device, indices.graphicsFamily.value(), 0, &graphicsQueue);
        vkGetDeviceQueue(device, indices.presentFamily.value(), 0, &presentQueue);
    }

    void createSwapchain() {
        VkSurfaceCapabilitiesKHR caps;
        vkGetPhysicalDeviceSurfaceCapabilitiesKHR(physicalDevice, surface, &caps);
        uint32_t formatCount = 0;
        vkGetPhysicalDeviceSurfaceFormatsKHR(physicalDevice, surface, &formatCount, nullptr);
        std::vector<VkSurfaceFormatKHR> formats(formatCount);
        vkGetPhysicalDeviceSurfaceFormatsKHR(physicalDevice, surface, &formatCount, formats.data());
        auto format = formats[0];
        for (const auto& candidate : formats) {
            if (candidate.format == VK_FORMAT_B8G8R8A8_SRGB && candidate.colorSpace == VK_COLOR_SPACE_SRGB_NONLINEAR_KHR) {
                format = candidate;
            }
        }
        swapchainFormat = format.format;
        swapchainExtent = caps.currentExtent.width != UINT32_MAX ? caps.currentExtent : VkExtent2D{WIDTH, HEIGHT};
        uint32_t imageCount = std::max(caps.minImageCount + 1, 2u);
        if (caps.maxImageCount > 0) imageCount = std::min(imageCount, caps.maxImageCount);
        auto indices = queueFamilies(physicalDevice, surface);
        std::array<uint32_t, 2> queueFamilyIndices = {indices.graphicsFamily.value(), indices.presentFamily.value()};
        VkSwapchainCreateInfoKHR info{};
        info.sType = VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR;
        info.surface = surface;
        info.minImageCount = imageCount;
        info.imageFormat = swapchainFormat;
        info.imageColorSpace = format.colorSpace;
        info.imageExtent = swapchainExtent;
        info.imageArrayLayers = 1;
        info.imageUsage = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT;
        if (indices.graphicsFamily != indices.presentFamily) {
            info.imageSharingMode = VK_SHARING_MODE_CONCURRENT;
            info.queueFamilyIndexCount = 2;
            info.pQueueFamilyIndices = queueFamilyIndices.data();
        } else {
            info.imageSharingMode = VK_SHARING_MODE_EXCLUSIVE;
        }
        info.preTransform = caps.currentTransform;
        info.compositeAlpha = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR;
        info.presentMode = VK_PRESENT_MODE_FIFO_KHR;
        info.clipped = VK_TRUE;
        if (vkCreateSwapchainKHR(device, &info, nullptr, &swapchain) != VK_SUCCESS) throw std::runtime_error("swapchain failed");
        vkGetSwapchainImagesKHR(device, swapchain, &imageCount, nullptr);
        swapchainImages.resize(imageCount);
        vkGetSwapchainImagesKHR(device, swapchain, &imageCount, swapchainImages.data());
        imageViews.resize(swapchainImages.size());
        for (size_t i = 0; i < swapchainImages.size(); ++i) {
            VkImageViewCreateInfo view{};
            view.sType = VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO;
            view.image = swapchainImages[i];
            view.viewType = VK_IMAGE_VIEW_TYPE_2D;
            view.format = swapchainFormat;
            view.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
            view.subresourceRange.levelCount = 1;
            view.subresourceRange.layerCount = 1;
            if (vkCreateImageView(device, &view, nullptr, &imageViews[i]) != VK_SUCCESS) throw std::runtime_error("image view failed");
        }
    }

    void createRenderPass() {
        VkAttachmentDescription color{};
        color.format = swapchainFormat;
        color.samples = VK_SAMPLE_COUNT_1_BIT;
        color.loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR;
        color.storeOp = VK_ATTACHMENT_STORE_OP_STORE;
        color.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
        color.finalLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR;
        VkAttachmentReference colorRef{};
        colorRef.attachment = 0;
        colorRef.layout = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL;
        VkSubpassDescription subpass{};
        subpass.pipelineBindPoint = VK_PIPELINE_BIND_POINT_GRAPHICS;
        subpass.colorAttachmentCount = 1;
        subpass.pColorAttachments = &colorRef;
        VkSubpassDependency dependency{};
        dependency.srcSubpass = VK_SUBPASS_EXTERNAL;
        dependency.dstSubpass = 0;
        dependency.srcStageMask = VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT;
        dependency.dstStageMask = VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT;
        dependency.dstAccessMask = VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT;
        VkRenderPassCreateInfo info{};
        info.sType = VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO;
        info.attachmentCount = 1;
        info.pAttachments = &color;
        info.subpassCount = 1;
        info.pSubpasses = &subpass;
        info.dependencyCount = 1;
        info.pDependencies = &dependency;
        if (vkCreateRenderPass(device, &info, nullptr, &renderPass) != VK_SUCCESS) throw std::runtime_error("render pass failed");
    }

    void createFramebuffers() {
        framebuffers.resize(imageViews.size());
        for (size_t i = 0; i < imageViews.size(); ++i) {
            VkImageView attachments[] = {imageViews[i]};
            VkFramebufferCreateInfo info{};
            info.sType = VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO;
            info.renderPass = renderPass;
            info.attachmentCount = 1;
            info.pAttachments = attachments;
            info.width = swapchainExtent.width;
            info.height = swapchainExtent.height;
            info.layers = 1;
            if (vkCreateFramebuffer(device, &info, nullptr, &framebuffers[i]) != VK_SUCCESS) throw std::runtime_error("framebuffer failed");
        }
    }

    void createCommandPool() {
        auto indices = queueFamilies(physicalDevice, surface);
        VkCommandPoolCreateInfo pool{};
        pool.sType = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO;
        pool.flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;
        pool.queueFamilyIndex = indices.graphicsFamily.value();
        if (vkCreateCommandPool(device, &pool, nullptr, &commandPool) != VK_SUCCESS) throw std::runtime_error("command pool failed");
        commandBuffers.resize(framebuffers.size());
        VkCommandBufferAllocateInfo alloc{};
        alloc.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;
        alloc.commandPool = commandPool;
        alloc.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
        alloc.commandBufferCount = static_cast<uint32_t>(commandBuffers.size());
        if (vkAllocateCommandBuffers(device, &alloc, commandBuffers.data()) != VK_SUCCESS) throw std::runtime_error("command buffer failed");
    }

    void createSync() {
        imageAvailable.resize(2);
        renderFinished.resize(2);
        inFlight.resize(2);
        VkSemaphoreCreateInfo sem{};
        sem.sType = VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO;
        VkFenceCreateInfo fence{};
        fence.sType = VK_STRUCTURE_TYPE_FENCE_CREATE_INFO;
        fence.flags = VK_FENCE_CREATE_SIGNALED_BIT;
        for (int i = 0; i < 2; ++i) {
            vkCreateSemaphore(device, &sem, nullptr, &imageAvailable[i]);
            vkCreateSemaphore(device, &sem, nullptr, &renderFinished[i]);
            vkCreateFence(device, &fence, nullptr, &inFlight[i]);
        }
    }

    void initImGui() {
        std::array<VkDescriptorPoolSize, 1> poolSizes = {{{VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER, 1000}}};
        VkDescriptorPoolCreateInfo pool{};
        pool.sType = VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO;
        pool.flags = VK_DESCRIPTOR_POOL_CREATE_FREE_DESCRIPTOR_SET_BIT;
        pool.maxSets = 1000;
        pool.poolSizeCount = static_cast<uint32_t>(poolSizes.size());
        pool.pPoolSizes = poolSizes.data();
        if (vkCreateDescriptorPool(device, &pool, nullptr, &descriptorPool) != VK_SUCCESS) throw std::runtime_error("descriptor pool failed");
        IMGUI_CHECKVERSION();
        ImGui::CreateContext();
        ImGui::StyleColorsDark();
        ImGui::GetStyle().WindowRounding = 8.0f;
        ImGui::GetStyle().FrameRounding = 6.0f;
        ImGui_ImplGlfw_InitForVulkan(window, true);
        auto indices = queueFamilies(physicalDevice, surface);
        ImGui_ImplVulkan_InitInfo init{};
        init.Instance = instance;
        init.PhysicalDevice = physicalDevice;
        init.Device = device;
        init.QueueFamily = indices.graphicsFamily.value();
        init.Queue = graphicsQueue;
        init.DescriptorPool = descriptorPool;
        init.RenderPass = renderPass;
        init.MinImageCount = 2;
        init.ImageCount = static_cast<uint32_t>(swapchainImages.size());
        init.MSAASamples = VK_SAMPLE_COUNT_1_BIT;
        ImGui_ImplVulkan_Init(&init);
    }

    void mainLoop() {
        while (!glfwWindowShouldClose(window)) {
            glfwPollEvents();
            drawFrame();
        }
        vkDeviceWaitIdle(device);
    }

    void buildUi() {
        ImGui::SetNextWindowPos(ImVec2(0, 0), ImGuiCond_Always);
        ImGui::SetNextWindowSize(ImGui::GetIO().DisplaySize, ImGuiCond_Always);
        ImGui::Begin("ReliQuary Brain Vault", nullptr, ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoResize);
        ImGui::Columns(3, nullptr, false);
        ImGui::SetColumnWidth(0, 360);
        ImGui::SetColumnWidth(1, 500);

        panelConfig();
        ImGui::NextColumn();
        panelGraph();
        ImGui::NextColumn();
        panelChat();
        ImGui::Columns(1);
        ImGui::End();
    }

    void inputText(const char* label, std::string& value, size_t cap = 512) {
        std::vector<char> buffer(cap);
        std::snprintf(buffer.data(), buffer.size(), "%s", value.c_str());
        if (ImGui::InputText(label, buffer.data(), buffer.size())) value = buffer.data();
    }

    void log(const std::string& message) {
        api.log.insert(api.log.begin(), message);
        if (api.log.size() > 18) api.log.pop_back();
    }

    void safeCall(const std::string& label, const std::function<void()>& fn) {
        try {
            fn();
        } catch (const std::exception& exc) {
            log(label + " failed: " + exc.what());
        }
    }

    void panelConfig() {
        ImGui::Text("Storage, Vault, Secret");
        inputText("API URL", api.apiUrl);
        inputText("Owner", api.owner);
        inputText("Vault name", api.vaultName);
        if (ImGui::Button("Create Vault", ImVec2(-1, 34))) {
            safeCall("Create vault", [&] {
                auto response = json::parse(postJson(api.apiUrl + "/vaults/", {
                    {"name", api.vaultName},
                    {"description", "ImGui Brain Vault"},
                    {"owner_id", api.owner},
                }));
                api.vaultId = response["vault_id"].get<std::string>();
                log("Vault created: " + api.vaultId);
            });
        }
        inputText("Vault ID", api.vaultId);
        inputText("Secret name", api.secretName);
        inputText("Secret value", api.secretValue);
        inputText("Secret password", api.secretPassword);
        if (ImGui::Button("Store Text Secret", ImVec2(-1, 34))) {
            safeCall("Store secret", [&] {
                postJson(api.apiUrl + "/vaults/secrets?vault_id=" + api.vaultId, {
                    {"secret_name", api.secretName},
                    {"secret_value", api.secretValue},
                    {"access_password", api.secretPassword},
                    {"metadata", {{"source", "vulkan-imgui"}}},
                });
                log("Text secret stored with specific password.");
            });
        }
        inputText("File or folder path", api.filePath);
        if (ImGui::Button("Store File/Folder Secret", ImVec2(-1, 34))) {
            safeCall("Store file/folder", [&] {
                postJson(api.apiUrl + "/vaults/secrets/file?vault_id=" + api.vaultId, {
                    {"secret_name", api.secretName},
                    {"path", api.filePath},
                    {"sensitivity", api.sensitivity},
                    {"access_password", api.secretPassword},
                });
                log("File/folder stored as encrypted secret payload.");
            });
        }
        inputText("Share password", api.sharePassword);
        if (ImGui::Button("Create Share Link", ImVec2(-1, 34))) {
            safeCall("Create share", [&] {
                auto response = json::parse(postJson(api.apiUrl + "/share/create", {
                    {"vault_id", api.vaultId},
                    {"secret_name", api.secretName},
                    {"created_by", api.owner},
                    {"ttl_minutes", 60},
                    {"max_views", 3},
                    {"share_password", api.sharePassword},
                }));
                api.shareToken = response["token"].get<std::string>();
                log("Share token: " + api.shareToken);
            });
        }
        inputText("Share token", api.shareToken);
    }

    void panelGraph() {
        ImGui::Text("Trust Graph");
        inputText("Requesting user", api.requestUser);
        inputText("Remote address", api.remoteAddress);
        ImGui::SliderInt("Trust score", &api.trustScore, 0, 100);
        ImGui::Checkbox("Device verified", &api.deviceVerified);
        ImGui::SameLine();
        ImGui::Checkbox("Local session", &api.localSession);
        ImGui::SameLine();
        ImGui::Checkbox("Biometric", &api.biometricVerified);
        const char* sensitivities[] = {"public", "private", "sensitive", "secret", "sealed"};
        int current = 3;
        for (int i = 0; i < 5; ++i) if (api.sensitivity == sensitivities[i]) current = i;
        if (ImGui::Combo("Sensitivity", &current, sensitivities, 5)) api.sensitivity = sensitivities[current];
        if (ImGui::Button("Ask Brain Vault", ImVec2(-1, 38))) {
            safeCall("Request secret", [&] {
                api.lastDecision = json::parse(postJson(api.apiUrl + "/access/request-secret", {
                    {"vault_id", api.vaultId},
                    {"resource_name", api.secretName},
                    {"sensitivity", api.sensitivity},
                    {"trust_score", api.trustScore},
                    {"access_password", api.secretPassword},
                    {"subject", {
                        {"user_id", api.requestUser},
                        {"device_verified", api.deviceVerified},
                        {"local_session", api.localSession},
                        {"biometric_verified", api.biometricVerified},
                        {"remote_address", api.remoteAddress},
                        {"user_agent", "reliquary-imgui"},
                    }},
                }));
                log("Decision: " + api.lastDecision.value("decision", "unknown"));
            });
        }
        if (ImGui::Button("Simulate Remote Attacker", ImVec2(-1, 34))) {
            api.requestUser = "remote-script";
            api.remoteAddress = "203.0.113.10";
            api.trustScore = 25;
            api.deviceVerified = false;
            api.localSession = false;
            api.biometricVerified = false;
        }

        ImDrawList* draw = ImGui::GetWindowDrawList();
        ImVec2 p = ImGui::GetCursorScreenPos();
        float w = ImGui::GetContentRegionAvail().x;
        drawNode(draw, ImVec2(p.x + 20, p.y + 38), ImVec2(120, 86), "Storage", IM_COL32(56, 74, 94, 255));
        ImU32 gateColor = IM_COL32(99, 107, 120, 255);
        std::string decision = api.lastDecision.value("decision", "waiting");
        if (decision == "allow") gateColor = IM_COL32(11, 110, 79, 255);
        if (decision == "redact") gateColor = IM_COL32(170, 95, 0, 255);
        if (decision == "deny") gateColor = IM_COL32(156, 31, 31, 255);
        drawNode(draw, ImVec2(p.x + w / 2 - 70, p.y + 22), ImVec2(140, 118), ("Gate\n" + decision).c_str(), gateColor);
        drawNode(draw, ImVec2(p.x + w - 150, p.y + 38), ImVec2(130, 86), "Answer", IM_COL32(56, 74, 94, 255));
        draw->AddLine(ImVec2(p.x + 140, p.y + 82), ImVec2(p.x + w / 2 - 70, p.y + 82), IM_COL32(220, 220, 220, 180), 3.0f);
        draw->AddLine(ImVec2(p.x + w / 2 + 70, p.y + 82), ImVec2(p.x + w - 150, p.y + 82), IM_COL32(220, 220, 220, 180), 3.0f);
        ImGui::Dummy(ImVec2(w, 170));
        ImGui::TextWrapped("Latest: %s", api.lastDecision.dump(2).c_str());
    }

    void drawNode(ImDrawList* draw, ImVec2 pos, ImVec2 size, const char* text, ImU32 color) {
        draw->AddRectFilled(pos, ImVec2(pos.x + size.x, pos.y + size.y), color, 12.0f);
        draw->AddRect(pos, ImVec2(pos.x + size.x, pos.y + size.y), IM_COL32(255, 255, 255, 80), 12.0f, 0, 2.0f);
        draw->AddText(ImVec2(pos.x + 14, pos.y + 16), IM_COL32(255, 255, 255, 255), text);
    }

    void panelChat() {
        ImGui::Text("Brain Chat");
        inputText("Prompt", api.chatInput, 1024);
        if (ImGui::Button("Send", ImVec2(-1, 34))) {
            if (api.chatInput.find("share") != std::string::npos) {
                log("Chat routed to share panel. Create a share link with expiry and password.");
            } else if (api.chatInput.find("file") != std::string::npos || api.chatInput.find("folder") != std::string::npos) {
                log("Chat routed to file/folder secret panel. Select a path and store it.");
            } else {
                log("Chat routed to trust gate. Use Ask Brain Vault for policy-gated reveal.");
            }
        }
        if (ImGui::Button("Refresh Events", ImVec2(-1, 34))) {
            safeCall("Events", [&] { log(getJson(api.apiUrl + "/access/events")); });
        }
        ImGui::Separator();
        for (const auto& item : api.log) ImGui::TextWrapped("%s", item.c_str());
    }

    void recordCommandBuffer(VkCommandBuffer cmd, uint32_t imageIndex) {
        VkCommandBufferBeginInfo begin{};
        begin.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
        vkBeginCommandBuffer(cmd, &begin);
        VkClearValue clear{};
        clear.color = {{0.035f, 0.043f, 0.055f, 1.0f}};
        VkRenderPassBeginInfo rp{};
        rp.sType = VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO;
        rp.renderPass = renderPass;
        rp.framebuffer = framebuffers[imageIndex];
        rp.renderArea.extent = swapchainExtent;
        rp.clearValueCount = 1;
        rp.pClearValues = &clear;
        vkCmdBeginRenderPass(cmd, &rp, VK_SUBPASS_CONTENTS_INLINE);
        ImGui_ImplVulkan_RenderDrawData(ImGui::GetDrawData(), cmd);
        vkCmdEndRenderPass(cmd);
        vkEndCommandBuffer(cmd);
    }

    void drawFrame() {
        vkWaitForFences(device, 1, &inFlight[currentFrame], VK_TRUE, UINT64_MAX);
        uint32_t imageIndex;
        vkAcquireNextImageKHR(device, swapchain, UINT64_MAX, imageAvailable[currentFrame], VK_NULL_HANDLE, &imageIndex);
        vkResetFences(device, 1, &inFlight[currentFrame]);
        vkResetCommandBuffer(commandBuffers[imageIndex], 0);

        ImGui_ImplVulkan_NewFrame();
        ImGui_ImplGlfw_NewFrame();
        ImGui::NewFrame();
        buildUi();
        ImGui::Render();
        recordCommandBuffer(commandBuffers[imageIndex], imageIndex);

        VkSemaphore waitSemaphores[] = {imageAvailable[currentFrame]};
        VkPipelineStageFlags waitStages[] = {VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT};
        VkSemaphore signalSemaphores[] = {renderFinished[currentFrame]};
        VkSubmitInfo submit{};
        submit.sType = VK_STRUCTURE_TYPE_SUBMIT_INFO;
        submit.waitSemaphoreCount = 1;
        submit.pWaitSemaphores = waitSemaphores;
        submit.pWaitDstStageMask = waitStages;
        submit.commandBufferCount = 1;
        submit.pCommandBuffers = &commandBuffers[imageIndex];
        submit.signalSemaphoreCount = 1;
        submit.pSignalSemaphores = signalSemaphores;
        if (vkQueueSubmit(graphicsQueue, 1, &submit, inFlight[currentFrame]) != VK_SUCCESS) throw std::runtime_error("queue submit failed");
        VkPresentInfoKHR present{};
        present.sType = VK_STRUCTURE_TYPE_PRESENT_INFO_KHR;
        present.waitSemaphoreCount = 1;
        present.pWaitSemaphores = signalSemaphores;
        present.swapchainCount = 1;
        present.pSwapchains = &swapchain;
        present.pImageIndices = &imageIndex;
        vkQueuePresentKHR(presentQueue, &present);
        currentFrame = (currentFrame + 1) % 2;
    }

    void cleanup() {
        ImGui_ImplVulkan_Shutdown();
        ImGui_ImplGlfw_Shutdown();
        ImGui::DestroyContext();
        for (int i = 0; i < 2; ++i) {
            vkDestroySemaphore(device, renderFinished[i], nullptr);
            vkDestroySemaphore(device, imageAvailable[i], nullptr);
            vkDestroyFence(device, inFlight[i], nullptr);
        }
        vkDestroyDescriptorPool(device, descriptorPool, nullptr);
        vkDestroyCommandPool(device, commandPool, nullptr);
        for (auto framebuffer : framebuffers) vkDestroyFramebuffer(device, framebuffer, nullptr);
        vkDestroyRenderPass(device, renderPass, nullptr);
        for (auto view : imageViews) vkDestroyImageView(device, view, nullptr);
        vkDestroySwapchainKHR(device, swapchain, nullptr);
        vkDestroyDevice(device, nullptr);
        vkDestroySurfaceKHR(instance, surface, nullptr);
        vkDestroyInstance(instance, nullptr);
        glfwDestroyWindow(window);
        glfwTerminate();
    }
};

}  // namespace

int main() {
    curl_global_init(CURL_GLOBAL_DEFAULT);
    try {
        VulkanImGuiApp().run();
        curl_global_cleanup();
        return 0;
    } catch (const std::exception& exc) {
        std::cerr << "ReliQuary Vulkan ImGui failed: " << exc.what() << "\n";
        curl_global_cleanup();
        return 1;
    }
}
