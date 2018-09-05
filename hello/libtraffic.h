typedef void* traffic_generator_instance_t;
extern "C" traffic_generator_instance_t traffic_generator_init(const char* config_str);
extern "C" int traffic_generator_get_frame(traffic_generator_instance_t tg_id, uint32_t* len, uint8_t** data, uint64_t* tx_time_sec, uint32_t* tx_time_nsec);

