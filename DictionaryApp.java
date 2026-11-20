import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

public class DictionaryApp {
    public static void main(String[] args) {
        Map<String, String> dictionary = new HashMap<>();
        dictionary.put("android", "An open-source OS for smartphones.");
        dictionary.put("java", "Programming language for Android.");
        dictionary.put("intent", "Message object for Android components.");

        Scanner sc = new Scanner(System.in);
        System.out.print("Enter word: ");
        String word = sc.nextLine().toLowerCase();

        String meaning = dictionary.getOrDefault(word, "Word not found.");
        System.out.println(word + " : " + meaning);
        sc.close();
    }
}
