#include <vulkan/vulkan.h>

#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

namespace {

struct AccessEvent {
    std::string decision;
    std::string resource;
    int trust = 0;
    int required = 0;
};

VkInstance createInstance() {
    VkApplicationInfo appInfo{};
    appInfo.sType = VK_STRUCTURE_TYPE_APPLICATION_INFO;
    appInfo.pApplicationName = "ReliQuary Brain Vault Visualizer";
    appInfo.applicationVersion = VK_MAKE_VERSION(0, 1, 0);
    appInfo.pEngineName = "ReliQuary Vulkan";
    appInfo.engineVersion = VK_MAKE_VERSION(0, 1, 0);
    appInfo.apiVersion = VK_API_VERSION_1_1;

    VkInstanceCreateInfo createInfo{};
    createInfo.sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO;
    createInfo.pApplicationInfo = &appInfo;

    VkInstance instance = VK_NULL_HANDLE;
    VkResult result = vkCreateInstance(&createInfo, nullptr, &instance);
    if (result != VK_SUCCESS) {
        throw std::runtime_error("vkCreateInstance failed. Install Vulkan SDK with MoltenVK on macOS.");
    }
    return instance;
}

std::vector<AccessEvent> demoEvents() {
    return {
        {"allow", "apple-password-note", 99, 90},
        {"redact", "passport-scan-path", 68, 75},
        {"deny", "s3-root-token", 10, 90},
        {"allow", "public-project-readme", 5, 0},
    };
}

std::string bar(int value, int width = 24) {
    int filled = std::clamp(value * width / 100, 0, width);
    return std::string(filled, '#') + std::string(width - filled, '.');
}

void renderFrame(const AccessEvent& event, std::size_t frame) {
    const char* color = "\033[37m";
    if (event.decision == "allow") color = "\033[32m";
    if (event.decision == "redact") color = "\033[33m";
    if (event.decision == "deny") color = "\033[31m";

    std::cout << "\033[2J\033[H";
    std::cout << "ReliQuary Vulkan Brain Vault Visualizer\n";
    std::cout << "Frame " << frame << " | Vulkan instance active | Ctrl+C to quit\n\n";
    std::cout << "          [Storage]\n";
    std::cout << "              |\n";
    std::cout << "              v\n";
    std::cout << color << "       [Trust Gate: " << event.decision << "]\033[0m\n";
    std::cout << "              |\n";
    std::cout << "              v\n";
    std::cout << "          [Answer]\n\n";
    std::cout << "Resource: " << event.resource << "\n";
    std::cout << "Trust:    [" << bar(event.trust) << "] " << event.trust << "\n";
    std::cout << "Required: [" << bar(event.required) << "] " << event.required << "\n\n";
    std::cout << "Next phase: replace terminal renderer with swapchain + ImGui graph nodes.\n";
}

}  // namespace

int main() {
    try {
        VkInstance instance = createInstance();
        auto events = demoEvents();
        for (std::size_t frame = 0; frame < 120; ++frame) {
            renderFrame(events[frame % events.size()], frame);
            std::this_thread::sleep_for(std::chrono::milliseconds(250));
        }
        vkDestroyInstance(instance, nullptr);
        return EXIT_SUCCESS;
    } catch (const std::exception& exc) {
        std::cerr << "ReliQuary Vulkan visualizer failed: " << exc.what() << "\n";
        return EXIT_FAILURE;
    }
}
