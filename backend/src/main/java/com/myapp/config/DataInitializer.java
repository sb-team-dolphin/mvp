package com.myapp.config;

import com.myapp.model.User;
import com.myapp.repository.UserRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DataInitializer {

    @Bean
    CommandLineRunner initDatabase(UserRepository repository) {
        return args -> {
            // 데이터가 없을 때만 초기 데이터 삽입
            if (repository.count() == 0) {
                repository.save(new User(null, "Alice Johnson", "alice@example.com", "Developer"));
                repository.save(new User(null, "Bob Smith", "bob@example.com", "Designer"));
                repository.save(new User(null, "Charlie Brown", "charlie@example.com", "Manager"));
                System.out.println("Initial data loaded successfully!");
            }
        };
    }
}
