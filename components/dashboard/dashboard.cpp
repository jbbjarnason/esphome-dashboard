#include "dashboard.h"
#include "esphome/core/util.h"
#include "esphome/core/log.h"
#include "esphome/components/network/util.h"

using namespace esphome::dashboard;

static const char *const TAG = "dashboard";

Dashboard::Dashboard(web_server_base::WebServerBase *base):
  ESPDash(),
  base_(base)
{
}

Dashboard::~Dashboard() {
  base_->deinit();
}

void Dashboard::setup() {
  base_->init();
  ESPDash::init(base_->get_server());
}
void Dashboard::dump_config() {
  ESP_LOGCONFIG(TAG, "Web Server:");
  ESP_LOGCONFIG(TAG, "  Address: %s:%u", esphome::network::get_ip_address().str().c_str(), base_->get_port());
}
