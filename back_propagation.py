import tkinter as tk

# Geometry constants.
WINDOW_WID = 910
WINDOW_HGT = 610
FRAME1_WID = 150
PADX = 5
NETWORK_CANVAS_WID = WINDOW_WID - FRAME1_WID - 4 * PADX
NETWORK_CANVAS_HGT = WINDOW_HGT - 2 * PADX

class App:
    # Create and manage the tkinter interface.
    def __init__(self):
        self.network = None

        # Make the main interface.
        self.window = tk.Tk()
        self.window.title('back_propagation')
        self.window.protocol('WM_DELETE_WINDOW', self.kill_callback)
        self.window.geometry(f'{WINDOW_WID}x{WINDOW_HGT}')

        # Build the UI.
        self.build_ui()

        # Load the data.
        self.load_data()

        # Draw the network.
        self.redraw_network()

        # Display the window.
        self.window.focus_force()
        self.window.mainloop()

    # Build an odd/even test network.
    def load_data(self):
        # Build the network.
        self.network = NeuralNet([3, 4, 2])

        # Set synapse weights.
        weights = [
            [
                # Input layer.
                #  000   101   110   011
                [ -100,   10,   10, -100],  # Neuron 0
                [ -100, -100,   10,   10],  # Neuron 1
                [ -100,   10, -100,   10],  # Neuron 2
                [    5,  -15,  -15,  -15],  # Bias
            ],
            [
                # Hidden layer.
                # Odd  Even
                [ -10,  10 ],  # Neuron 0: 000
                [ -10,  10 ],  # Neuron 1: 101
                [ -10,  10 ],  # Neuron 2: 110
                [ -10,  10 ],  # Neuron 3: 011
                [   5,  -5 ],  # Bias
            ]
        ]
        self.set_synapse_weights(self.network.all_layers, weights)
        
        # Display the network.
        #self.network.dump()

    # Set the weights for the synapses in all layers.
    def set_synapse_weights(self, all_layers, weights):
        for layer_num in range(len(all_layers)):
            layer = all_layers[layer_num]
            for neuron_num in range(len(layer)):
                neuron = layer[neuron_num]
                for synapse_num in range(len(neuron.outputs)):
                    synapse = neuron.outputs[synapse_num]
                    synapse.weight = weights[layer_num][neuron_num][synapse_num]

    def build_ui(self):
        # Make controls to define the network.
        frame1 = tk.Frame(self.window, width=FRAME1_WID)
        frame1.pack(side=tk.LEFT, expand=False, fill=tk.Y, padx=PADX)
        frame1.pack_propagate(False)

        frame2 = tk.Frame(self.window)
        frame2.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=PADX)

        # Min and max synapse weights.
        self.min_weight_text = make_field(frame1, 'Min Weight:', 13, '-10', (0,5))
        self.max_weight_text = make_field(frame1, 'Max Weight:', 13, '10', (0,5))

        # Randomize button.
        randomize_button = tk.Button(frame1, width=11, text='Randomize', command=self.randomize)
        randomize_button.pack(side=tk.TOP, pady=(2,20))

        # Num epochs.
        self.epochs_text = make_field(frame1, 'Num Epochs:', 13, '10000', (0,5))

        # Epochs per tick.
        self.epochs_per_tick_text = make_field(frame1, 'Epochs Per Tick:', 13, '1000', (0,5))

        # Learning rate.
        self.learning_rate_text = make_field(frame1, 'Learning Rate:', 13, '0.5', (0,5))

        # Train button.
        train_button = tk.Button(frame1, width=11, text='Train', command=self.train)
        train_button.pack(side=tk.TOP, pady=(2,10))
        
        # Error Listbox
        error_label = tk.Label(frame1, text='Epoch Errors:', width=12, anchor=tk.W)
        error_label.pack(side=tk.TOP)

        error_frame = tk.Frame(frame1)
        error_frame.pack(side=tk.TOP)
        scrollbar = tk.Scrollbar(error_frame, orient="vertical")
        self.error_listbox = tk.Listbox(error_frame, width=20, yscrollcommand=scrollbar.set)
        self.error_listbox.pack(side=tk.LEFT)
        scrollbar.config(command=self.error_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Checkbuttons.
        check_frame = tk.Frame(frame1, width=200)
        check_frame.pack(side=tk.TOP, pady=(20,0))

        self.check0_value = tk.IntVar()
        check0 = tk.Checkbutton(check_frame, variable=self.check0_value,
            onvalue=1, offvalue=0, command=self.redraw_network)
        check0.pack(side=tk.LEFT)

        self.check1_value = tk.IntVar()
        check1 = tk.Checkbutton(check_frame, variable=self.check1_value,
            onvalue=1, offvalue=0, command=self.redraw_network)
        check1.pack(side=tk.LEFT)

        self.check2_value = tk.IntVar()
        check2 = tk.Checkbutton(check_frame, variable=self.check2_value,
            onvalue=1, offvalue=0, command=self.redraw_network)
        check2.pack(side=tk.LEFT)

        # Labels to display results.
        self.even_value = tk.StringVar()
        self.even_value.set('Even = True')
        even_label = tk.Label(frame1, textvariable=self.even_value, height=1)
        even_label.pack(side=tk.TOP)

        self.odd_value = tk.StringVar()
        self.odd_value.set('Odd = False')
        odd_label = tk.Label(frame1, textvariable=self.odd_value, height=1)
        odd_label.pack(side=tk.TOP)

        # Frame 2.
        # Network canvas.
        self.canvas = tk.Canvas(frame2, bg='white',
            borderwidth=0, highlightthickness=0, relief=tk.SUNKEN,
            width=NETWORK_CANVAS_WID, height=NETWORK_CANVAS_HGT)
        self.canvas.pack(side=tk.LEFT, anchor=tk.NW)

    # Redraw the network after the user changed a checkbutton.
    def redraw_network(self):
        # Evaluate with the current checkbutton values.
        input_values = [
            self.check0_value.get(),
            self.check1_value.get(),
            self.check2_value.get(),
        ]
        self.network.evaluate(input_values)

        # Display the results textually.
        if self.network.output_layer[0].output < 0.33:
            self.odd_value.set('Odd = False')
        elif self.network.output_layer[0].output > 0.67:
            self.odd_value.set('Odd = True')
        else:
            self.odd_value.set('??????')

        if self.network.output_layer[1].output < 0.33:
            self.even_value.set('Even = False')
        elif self.network.output_layer[1].output > 0.67:
            self.even_value.set('Even = True')
        else:
            self.even_value.set('??????')

        # Draw the network.
        draw_network(self.network, self.canvas)

    def kill_callback(self):
        self.window.destroy()

    # Randomize the network's synapse weights.
    def randomize(self):
        # Clear previous results.
        self.error_listbox.delete(0, tk.END)
        self.num_epochs_trained = 0

        # Randomize the synapses.
        min_weight = float(self.min_weight_text.get())
        max_weight = float(self.max_weight_text.get())
        self.network.randomize(min_weight, max_weight)
        self.redraw_network()

    # Train the network.
    def train(self):
        # Get parameters.
        num_epochs = int(self.epochs_text.get())
        epochs_per_tick = int(self.epochs_per_tick_text.get())
        learning_rate = float(self.learning_rate_text.get())
        inputs = [
            [0, 0, 0],
            [0, 0, 1],
            [0, 1, 0],
            [0, 1, 1],
            [1, 0, 0],
            [1, 0, 1],
            [1, 1, 0],
            [1, 1, 1],
        ]
        targets = [
            [0, 1],
            [1, 0],
            [1, 0],
            [0, 1],
            [1, 0],
            [0, 1],
            [0, 1],
            [1, 0],
        ]
        max_epoch = self.num_epochs_trained + num_epochs # Stop after this epoch.
        self.tick(inputs, targets, learning_rate, max_epoch, epochs_per_tick)

    # Train for {num_epochs} in batches of {epochs_per_tick}.
    def tick(self, inputs, targets, learning_rate, max_epoch, epochs_per_tick):
        # Train for {epochs_per_tick} epochs.
        epoch_error = self.network.train(inputs, targets, learning_rate, epochs_per_tick)

        # Display the latest error.
        self.num_epochs_trained += epochs_per_tick
        self.error_listbox.insert(tk.END, f'{self.num_epochs_trained}: {epoch_error:.8f}')
        self.error_listbox.see(tk.END)

        # Redraw the network.
        self.redraw_network()

        # Repeat in 10 milliseconds.
        if self.num_epochs_trained < max_epoch:
            self.window.after(10, self.tick, inputs, targets, learning_rate,
                max_epoch, epochs_per_tick)
