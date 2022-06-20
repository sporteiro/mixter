/* Sebastian Porteiro ITER
pipelines schema
*/
var pipes_blueprint = {
	"pipeline_type": {
		"gstreamer": {
			"input_1_type": {
				"none_1_src": "",
				"shm_1_src": {
					"options": ["video_1_src", "audio_1_src","color_format_1_src"],
					"output_type": {
						"none_sink":"",
						"file_sink": {
							"options": ["file_bitrate_sink", "file_duration_sink","file_path_sink","file_tmp_path_sink"]
						},
						"tcp_sink": {
							"options": ["tcp_ip_sink", "tcp_port_sink"]
						},
						"udp_sink": {
							"options": ["udp_ip_sink", "udp_port_sink"]
						},
						"udp_mpeg2_sink": {
							"options": ["udp_ip_sink", "udp_port_sink"]
						},
						"rtmp_sink": {
							"options": ["rtmp_url_sink"]
						},
						"shm_sink": {
							"options": ["video_sink", "audio_sink","color_format_sink"]
						},
						"window": ""

					}
				},
				"udp_1_src": {
					"options": ["udp_ip_1_src", "udp_port_1_src"],
					"output_type": {
						"none_sink":"",
						"file_sink": {
							"options": ["file_bitrate_sink", "file_duration_sink","file_path_sink","file_tmp_path_sink"]
						},
						"window": ""
					}
				},
				"rtp_1_src": {
					"options": ["udp_ip_1_src", "udp_port_1_src"],
					"output_type": {
						"none_sink":"",
						"file_sink": {
							"options": ["file_bitrate_sink", "file_duration_sink","file_path_sink","file_tmp_path_sink"]
						},
						"window": ""
					}
				},
				"tcp_1_src": {
					"options": ["tcp_ip_1_src", "tcp_port_1_src"],
					"output_type": {
						"none_sink":"",
						"window": ""
					}
				},
				"file_1_src": {
					"options": ["file_1_src"],
					"output_type": {
						"none_sink":"",
						"window": "",
						"shm_sink": {
							"options": ["video_sink", "audio_sink","color_format_sink"]
						},
					}
				},
				"videotest_1_src": {
					"options": ["pattern"],
					"output_type": {
						"none_sink":"",
						"window": "",
						"shm_sink": {
							"options": ["video_sink", "audio_sink","color_format_sink"]
						},
					}
				},
				"ximage_1_src": {
					"options": ["startx","starty","endx","endy"],
					"output_type": {
						"none_sink":"",
						"window": "",
						"file_sink": {
							"options": ["file_path_sink"]
						},
					}
				},
				"v4l2_1_src": {
					"output_type": {
						"none_sink":"",
						"window": "",
						"file_sink": {
							"options": ["file_path_sink"]
						},
					}
				}
			},
			"input_2_type": {
				"none_2_src": "",
				"udp_2_src": {
					"options": ["udp_ip_2_src", "udp_port_2_src"]
				},
                "file_2_src": {
					"options": ["file_path_2_src"],
				}
			}
		},
		"ffmpeg": {
			"input_1_type": {
				"none_1_src": "",
				"udp_1_src": {
                    "name": "UDP",
					"options": ["udp_ip_1_src", "udp_port_1_src"],
					"output_type": {
						"none_sink":"",
						"udp_sink": {
							"options": ["udp_ip_sink", "udp_port_sink"]
						}
					}
				},
				"tcp_1_src": {
					"options": ["tcp_ip_1_src", "tcp_port_1_src"],
					"output_type": {
						"none_sink":"",
						"udp_sink": {
							"options": ["udp_ip_sink", "udp_port_sink"]
						}
					}
				}
			},
			"input_2_type": {
				"none_2_src": "",
            }
		}
	}
}
