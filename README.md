As part of my 10-month internship, I developed a neurofeedback application to analyze whether individual preferences regarding the type of feedback influence the success rate of neurofeedback training. 

The experimental setup consists of pre- and post-training baseline recordings and five neurofeedback training blocks per session. 

For the application's general processing pipeline, I used YAML, which allowed me to process the participants' alpha waves in real-time. 

I used Python to develop specific nodes for my YAML processing pipeline, such as discrete LSL streams for alpha, beta, and theta waves and prompts that provide participants with instructions. The subsequent data analysis was also written in Python and executed in Jupyter Notebook. 
