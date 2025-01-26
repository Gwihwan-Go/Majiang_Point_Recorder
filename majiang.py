import tkinter as tk
from tkinter import ttk

BONUS_WIN_TYPES = ["暗杠", "明杠"]

class MajiangPointRecorder:
    def __init__(self, player_names):
        self.players = player_names
        self.scores = {player: 0 for player in self.players}
        self.boss_index = 0
        self.point_multipliers = {
            "wins": {"自己起窟窿":4,"自己起边赢":2, "边赢": 1, "窟窿": 2, "暗杠": 2, "明杠": 1},
        }
        self.game_history = []
        self.state_history = []

    def reset_game(self, new_boss_index=0, new_scores=None):
        """
        Resets the game with the option to specify a new boss and point distribution.
        
        :param new_boss_index: Index of the new boss in the players list.
        :param new_scores: Optional dictionary to set specific scores for players.
        """
        history_str = "" 
        if new_boss_index != self.boss_index :
            self.boss_index = new_boss_index
            history_str+=f"boss_idx from {self.boss_index} to {new_boss_index}"
        if new_scores is None:
            self.scores = {player: score for player, score in zip(self.players, self.scores)}
        else:
            self.scores = {player : score for player, score in zip(self.players, new_scores)}
            history_str+=f"scores from {list(self.scores.values())} to {new_scores}"
        self.game_history.append(history_str)
        # self.game_history = []  # Optionally reset or maintain history

    def set_boss(self, player):
        """Sets the boss (player who starts) for the round."""
        if player in self.scores:
            self.boss = player
        else:
            raise ValueError("Invalid player")

    def save_state(self, explanation=None):
        # Save the current state of the game
        state = {
            "scores": self.scores.copy(),
            "boss_index": self.boss_index,
            # Add more attributes as needed
        }
        self.state_history.append(state)
        if explanation:
            self.game_history.append(explanation + f"分数： {self.scores}")

    def unset(self):
        # Revert to the previous state if available
        if len(self.state_history) > 0:  # Ensure there's a previous state to revert to
            self.state_history.pop()  # Remove the current state
            self.game_history.pop()  # Remove the current history
            previous_state = self.state_history[-1] if len(self.state_history) > 0 else None
            if previous_state:
                self.scores = previous_state["scores"]
                self.boss_index = previous_state["boss_index"]
                # Revert other attributes as necessary
                print("Reverted to previous state:", self.scores)

        else:
            self.scores = {player: 0 for player in self.players}
            self.boss_index = 0
            print("No previous state to revert to.")


    def repay_points(self, giver, points, receiver):
        """Transfers points from one player to another."""
        self.scores[giver] += points
        self.scores[receiver] -= points
        self.save_state(f"{giver} gave {points} points to {receiver}.")

    def is_bonus(self, win_type):
        return win_type in BONUS_WIN_TYPES
    
    def record_round(self, winner, win_types, bonus=None):
        """Records a win, calculates, and updates scores based on the win type and if the winner is the boss, ensuring the total point sum remains 0."""
        boss = self.players[self.boss_index]
        pass_boss = False  # Determine if the boss position should pass based on non-bonus wins
        multipliers = 1  # Default multiplier for special win types

        # Initialize win_points calculation
        win_points = 0
        for win_type in win_types.split(","):
            # Calculate base win points for each win type, adjusted by multipliers
            base_points = self.point_multipliers["wins"][win_type] * multipliers

            for player in self.players:
                if player == winner:
                    # Winner's point gain calculation
                    continue  # Placeholder, actual calculation will be done after iterating through all players
                else:
                    # Losers' point deduction
                    boss_multiplier = 2 if (boss in [player, winner]) and not self.is_bonus(win_type) else 1
                    deduction = base_points * boss_multiplier
                    win_points += deduction  # Accumulate total points to be distributed to the winner
                    self.scores[player] -= deduction

            # Apply the calculated win_points to the winner
            self.scores[winner] += win_points

            if boss != winner and not self.is_bonus(win_type):
                pass_boss = True

        # Ensure the sum of points is zero
        assert sum(self.scores.values()) == 0, f"Total points do not sum to 0 after round. {self.scores}"

        # Update game history and potentially pass the boss position
        self.save_state(f"{winner} (庄家: {self.get_current_boss()}) 赢 {win_points} 分，胡的类型 ： {win_types}.")
        if pass_boss:
            self.boss_index = (self.boss_index + 1) % len(self.players)

    def get_current_boss(self):
        return self.players[self.boss_index]
    
    def get_scores(self):
        """Returns the current scores of all players."""
        return self.scores


class MajiangPointRecorderUI:
    def __init__(self, master=0):
        self.master = master
        self.player_names = ["东", "北", "西", "南"]
        self.submit_btn = None
        self.setup_initial_ui()
        self.recorder = None  # Instance of the game logic
        self.boss_var = tk.StringVar() 
    def setup_initial_ui(self):
        self.master.title("Enter Player Names")
        self.name_vars = [tk.StringVar() for _ in range(4)]
        self.name_entry_widgets = []

        for i, name_var in enumerate(self.name_vars):
            entry_frame = ttk.Frame(self.master)
            entry_frame.pack(pady=2)
            ttk.Label(entry_frame, text=f"Player {i+1} Name:").pack(side=tk.LEFT)
            entry = ttk.Entry(entry_frame, textvariable=name_var)
            entry.pack(side=tk.LEFT)
            self.name_entry_widgets.append(entry_frame)

        self.submit_btn = ttk.Button(self.master, text="Start Game", command=self.initialize_game_ui)
        self.submit_btn.pack(pady=10)
        
    def initialize_game_ui(self):
        self.player_names = [name_var.get() for name_var in self.name_vars]
        
        # Remove or destroy the initial UI components
        for widget in self.name_entry_widgets:
            widget.destroy()  # Use destroy to completely remove the widget
        # Assuming you have a method to setup the main game UI
        self.recorder = MajiangPointRecorder(self.player_names)
        self.setup_ui(self.player_names)
    def setup_ui(self, player_names):
        self.master.title("Majiang Point Recorder")

        self.submit_btn.destroy()
        self.player_score_vars = {}
        # Winner and Win Type Selection
        # Winner and Win Type Selection replaced with Checkbuttons
        winner_frame = ttk.Frame(self.master)
        winner_frame.pack(pady=(10, 5))  # Add padding above and below the frame
        ttk.Label(winner_frame, text="赢家:").pack(side=tk.LEFT, padx=(0, 10))  # Space after label
        self.winner_vars = {name : tk.BooleanVar() for name in player_names}
        for text, var in self.winner_vars.items():
            ttk.Checkbutton(winner_frame, text=text, variable=var).pack(side=tk.LEFT, padx=5)

        # Win Type Selection with Checkbuttons placed horizontally and spaced out
        win_type_frame = ttk.Frame(self.master)
        win_type_frame.pack(pady=(5, 10))  # Add padding above and below the frame
        ttk.Label(win_type_frame, text="胡的类型:").pack(side=tk.LEFT, padx=(0, 10))  # Space after label
        self.win_type_vars = {name : tk.BooleanVar() for name in self.recorder.point_multipliers['wins'].keys()}
        for text, var in self.win_type_vars.items():
            ttk.Checkbutton(win_type_frame, text=text, variable=var).pack(side=tk.LEFT, padx=5)

        ttk.Label(self.master, text="壮家:").pack()
        self.boss_label = ttk.Label(self.master, textvariable=self.boss_var)
        self.boss_label.pack()
        
        # Update the boss display with the initial boss
        self.update_boss_display()

        # Submit Button
        self.submit_button = tk.Button(self.master, text="回撤", command=self.submit_round)
        self.submit_button.pack()

        # Display Area for Boss, Points, and History
        self.display_area = tk.Text(self.master, height=30, width=60)
        self.display_area.pack()


        # In the MajiangPointRecorderUI class, add to the setup_ui method:

        self.giver_vars = {player: tk.BooleanVar() for player in self.recorder.players}
        self.receiver_vars = {player: tk.BooleanVar() for player in self.recorder.players}
        self.points_var = tk.StringVar()
        # Giver Selection
        ttk.Label(self.master, text="Giver:").pack()
        giver_frame = ttk.Frame(self.master)
        giver_frame.pack(pady=(5, 10))
        for player, var in self.giver_vars.items():
            ttk.Checkbutton(giver_frame, text=player, variable=var).pack(side=tk.LEFT, padx=5)

        # Receiver Selection
        ttk.Label(self.master, text="Receiver:").pack()
        receiver_frame = ttk.Frame(self.master)
        receiver_frame.pack(pady=(5, 10))
        for player, var in self.receiver_vars.items():
            ttk.Checkbutton(receiver_frame, text=player, variable=var).pack(side=tk.LEFT, padx=5)

        # Frame for Points Entry and Repay Points Button
        points_frame = ttk.Frame(self.master)
        points_frame.pack(pady=5, fill='x')

        # Points Label and Entry
        ttk.Label(points_frame, text="Points:").pack(side=tk.LEFT, padx=5)
        self.points_var = tk.StringVar()
        self.points_entry = ttk.Entry(points_frame, textvariable=self.points_var)
        self.points_entry.pack(side=tk.LEFT, padx=5)

        # Repay Points Button
        self.repay_button = ttk.Button(points_frame, text="Repay Points", command=self.repay_points)
        self.repay_button.pack(side=tk.LEFT, padx=5)

        boss_frame = ttk.Frame(self.master)
        boss_frame.pack(pady=5, fill='x')
        ttk.Label(boss_frame, text="Reset 壮:").pack(side=tk.LEFT, padx=5)
        self.new_boss_var = tk.StringVar()
        self.new_boss_combobox = ttk.Combobox(boss_frame, textvariable=self.new_boss_var, values=self.recorder.players)
        self.new_boss_combobox.pack(side=tk.LEFT)

        # Frame for New Scores Input for Each Player
        scores_frame = ttk.Frame(self.master)
        scores_frame.pack(pady=5, fill='x')
        ttk.Label(scores_frame, text="分数:").pack(side=tk.LEFT, padx=5)

        scores_entry_frame = ttk.Frame(scores_frame)
        scores_entry_frame.pack(side=tk.LEFT, fill='x', expand=True)
        
        for player in self.recorder.players:
            player_frame = ttk.Frame(scores_entry_frame)
            player_frame.pack(side=tk.LEFT, padx=10)
            ttk.Label(player_frame, text=f"{player}:").pack(side=tk.LEFT)
            score_var = tk.StringVar()
            ttk.Entry(player_frame, textvariable=score_var, width=5).pack(side=tk.LEFT)
            self.player_score_vars[player] = score_var

        # Reset Game Button
        self.reset_game_button = tk.Button(self.master, text="Reset Game", command=self.reset_game)
        self.reset_game_button.pack()

        self.unset_btn = tk.Button(self.master, text="Undo", command=self.unset)
        self.unset_btn.pack()

    def unset(self):
        self.recorder.unset()
        self.update_display()

    def reset_game(self):
        """Resets the game with the selected new boss and updates the display."""
        new_boss_index = self.recorder.players.index(self.new_boss_combobox.get()) if self.new_boss_combobox.get() in self.recorder.players else self.recorder.boss_index
        print(self.player_score_vars)
        self.recorder.reset_game(new_boss_index=new_boss_index, new_scores=[int(score.get()) for score in self.player_score_vars.values()])
        self.update_display()

    def update_boss_display(self):
        # Update the boss_var with the current boss's name
        current_boss = self.recorder.get_current_boss()
        self.boss_var.set(current_boss)

    def repay_points(self):
        selected_givers = [player for player, var in self.giver_vars.items() if var.get()]
        selected_receivers = [player for player, var in self.receiver_vars.items() if var.get()]
        try:
            points = int(self.points_entry.get())
            self.recorder.repay_points(selected_givers[0], points, selected_receivers[0])
            # For simplicity, this example will just print the selections
            # Real logic will depend on how you want to handle multiple selections
            if selected_givers and selected_receivers:
                print(f"Givers: {selected_givers}, Receivers: {selected_receivers}, Points: {points}")
                # Implement your logic to handle repayments here
                self.update_display()  # Refresh the display to show the updated scores and history
            else:
                print("Please select at least one giver and one receiver.")
        except ValueError:
            print("Invalid number of points.")


    def submit_round(self):
        selected_winners = [winner for winner, var in self.winner_vars.items() if var.get()]
        # Collecting selected win types
        selected_win_types = [win_type for win_type, var in self.win_type_vars.items() if var.get()]
        
        # For simplicity, let's assume only one winner and win type can be selected for now,
        # but this can be adjusted based on your game's rules.
        winner = ','.join(selected_winners)  # Joining multiple selections if necessary
        win_type = ','.join(selected_win_types)  # Joining multiple selections if necessary
        
        # Assume we handle bonus input correctly
        bonus = None  # Placeholder for bonus logic

        self.recorder.record_round(winner, win_type, bonus)
        self.update_display()

    def reset_btns(self):
        for var in self.winner_vars.values():
            var.set(False)
        for var in self.win_type_vars.values():
            var.set(False)
        for var in self.giver_vars.values():
            var.set(False)
        for var in self.receiver_vars.values():
            var.set(False)

    def update_display(self):
        self.reset_btns()   
        current_scores = self.recorder.get_scores()
        current_boss = self.recorder.get_current_boss()
        self.update_boss_display()
        history_text = "\n".join(self.recorder.game_history)
        display_text = f"当前庄家: {current_boss}\n分数:\n" + "\n".join([f"{player}: {score}" for player, score in current_scores.items()]) + "\n\nHistory:\n" + history_text
        self.display_area.delete('1.0', tk.END)
        self.display_area.insert(tk.END, display_text)

if __name__ == "__main__":
    """
        东(1)
   (2)北    南(4)
        西(3)
    """

    root = tk.Tk()
    app = MajiangPointRecorderUI(root)
    root.mainloop()
